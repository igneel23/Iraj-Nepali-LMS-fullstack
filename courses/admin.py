from django.contrib import admin
from .models import (
    Course, Category, WhatYouWillLearn, Requirement, WhoIsFor, CourseReview
)

# Inline models to show related data inside the course admin
class WhatYouWillLearnInline(admin.TabularInline):
    model = WhatYouWillLearn
    extra = 1
    min_num = 1


class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 1
    min_num = 1


class WhoIsForInline(admin.TabularInline):
    model = WhoIsFor
    extra = 1
    min_num = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'mentor', 'category', 'level', 'language', 'actual_price',
        'discounted_price', 'is_discount_active', 'is_live', 'is_published', 'start_date'
    )
    search_fields = ('title', 'mentor__username', 'category__name')
    list_filter = ('level', 'language', 'is_live', 'is_discount_active', 'is_published')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    # These are the correct fields in your model ✅
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'mentor', 'category', 'short_description', 'description', 'thumbnail')
        }),
        ('Pricing', {
            'fields': ('actual_price', 'discounted_price', 'is_discount_active')
        }),
        ('Schedule & Duration', {
            'fields': ('start_date', 'live_days', 'live_time', 'total_hours', 'language', 'level')
        }),
        ('Enrollment', {
            'fields': ('total_seats', 'enrolled_students', 'is_live')
        }),
        ('Status & Ratings', {
            'fields': ('is_published', 'rating_avg', 'rating_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    inlines = [WhatYouWillLearnInline, RequirementInline, WhoIsForInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'created_at')
    search_fields = ('course__title', 'student__username')
    list_filter = ('rating', 'created_at')
