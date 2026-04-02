import os
import uuid
from django.contrib import admin
from .models import Certificate, StudentCertificate
from .utils.certificate_generator import generate_certificate_pdf as generate_certificate
from django.conf import settings
from datetime import date
from enrollments.models import Enrollment
from users.models import User


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('course', 'is_published')
    list_filter = ('is_published', 'course')
    search_fields = ('course__title',)
    actions = ['publish_certificates']

    def save_model(self, request, obj, form, change):
        """
        Auto-generate and publish certificates when a new Certificate object is created.
        """
        super().save_model(request, obj, form, change)

        if not obj.is_published:
            obj.is_published = True
            obj.save()

        self._generate_certificates(obj)

    def publish_certificates(self, request, queryset):
        """
        Bulk action to publish selected certificates and issue them to verified students.
        """
        for certificate in queryset:
            if not certificate.is_published:
                certificate.is_published = True
                certificate.save()

            self._generate_certificates(certificate)

        self.message_user(request, "✅ Certificates have been generated and issued to verified students.")

    def _generate_certificates(self, certificate_obj):
        """
        Generate and save certificates for verified students with unique registration numbers.
        """
        enrolled_students = Enrollment.objects.filter(course=certificate_obj.course, status='verified')

        cert_folder = os.path.join(settings.MEDIA_ROOT, 'certificates')
        os.makedirs(cert_folder, exist_ok=True)

        for enrollment in enrolled_students:
            try:
                student_user = User.objects.get(email=enrollment.email)
            except User.DoesNotExist:
                continue

            student_name = f"{enrollment.first_name} {enrollment.last_name}"

            # Generate a unique registration number (8-digit alphanumeric)
            registration_number = f"REG-{uuid.uuid4().hex[:8].upper()}"

            # Include random short suffix in filename to prevent overwrite
            filename = f"{enrollment.first_name}_{certificate_obj.course.title}_{uuid.uuid4().hex[:6]}.pdf"

            # Generate and save the PDF certificate
            output_path = generate_certificate(
                student_name=student_name,
                registration_number=registration_number,
                output_filename=filename,
                template_path=certificate_obj.template_file.path
            )

            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)

            # Save/update StudentCertificate
            StudentCertificate.objects.update_or_create(
                certificate=certificate_obj,
                student=student_user,
                defaults={
                    'status': 'issued',
                    'download_link': relative_path,
                    'unique_id': registration_number  # unique for each certificate
                }
            )

    publish_certificates.short_description = "Publish and issue selected certificates to verified students"


@admin.register(StudentCertificate)
class StudentCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'get_student_name', 'unique_id', 'issued_on', 'status')
    list_filter = ('certificate', 'status')
    search_fields = ('student__first_name', 'student__last_name', 'certificate__course__title', 'unique_id')
    readonly_fields = ('unique_id', 'issued_on')

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    get_student_name.short_description = "Student Name"
