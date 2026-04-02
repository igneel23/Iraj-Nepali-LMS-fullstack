from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import BlogCategory, BlogPost, BlogTag, Comment
from ckeditor_uploader.widgets import CKEditorUploadingWidget  # ✅ correct widget import


# ----------------------------------------
# 📝 Custom Form for CKEditor Integration
# ----------------------------------------
class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'content': CKEditorUploadingWidget(),  # ✅ enables upload button in toolbar
        }


# ----------------------------------------
# 🧠 BlogPost Admin
# ----------------------------------------
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm

    list_display = (
        "thumbnail_preview",
        "title",
        "author",
        "category",
        "status",
        "is_published",
        "views",
        "published_at",
    )
    list_filter = ("status", "is_published", "category", "created_at")
    search_fields = ("title", "meta_title", "meta_description", "keywords")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    readonly_fields = ("views", "created_at", "updated_at", "meta_preview", "thumbnail_preview")

    fieldsets = (
        ("🧾 Basic Info", {
            "fields": ("title", "slug", "author", "category", "status", "is_published", "featured_image", "thumbnail_preview")
        }),
        ("✍️ Content", {
            "fields": ("excerpt", "content", "read_time")
        }),
        ("🔍 SEO Settings", {
            "fields": ("meta_title", "meta_description", "keywords", "meta_preview"),
            "description": "This section controls how your post appears in search engines and social previews."
        }),
        ("📊 Stats & Dates", {
            "fields": ("views", "created_at", "updated_at", "published_at")
        }),
    )

    # ----------------------------------------
    # 🖼️ Thumbnail preview method
    # ----------------------------------------
    def thumbnail_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width:70px; height:70px; object-fit:cover; border-radius:8px;" />',
                obj.featured_image.url,
            )
        return "—"
    thumbnail_preview.short_description = "Thumbnail"

    # ----------------------------------------
    # 🌐 SEO Live Meta Preview
    # ----------------------------------------
    def meta_preview(self, obj):
        title = obj.meta_title or "Meta title preview"
        desc = obj.meta_description or "Your SEO description will appear here."
        url = f"https://www.example.com/blog/{obj.slug or 'your-post-slug'}"

        return format_html(
            f"""
            <div style='
                border:1px solid #ddd;
                border-radius:8px;
                padding:12px;
                background:#fff;
                margin-top:5px;
                box-shadow:0 1px 2px rgba(0,0,0,0.05);
                font-family:Arial, sans-serif;
            '>
                <div style='color:#202124; font-size:18px; font-weight:500;' id='meta-title-preview'>{title}</div>
                <div style='color:#006621; font-size:14px; margin:4px 0;'>{url}</div>
                <div style='color:#4d5156; font-size:13px; line-height:1.4;' id='meta-desc-preview'>{desc}</div>
            </div>
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    const titleField = document.getElementById("id_meta_title");
                    const descField = document.getElementById("id_meta_description");
                    if (titleField) {{
                        titleField.addEventListener("input", () => {{
                            document.getElementById("meta-title-preview").innerText = titleField.value || "Meta title preview";
                        }});
                    }}
                    if (descField) {{
                        descField.addEventListener("input", () => {{
                            document.getElementById("meta-desc-preview").innerText = descField.value || "Your SEO description will appear here.";
                        }});
                    }}
                }});
            </script>
            """
        )
    meta_preview.short_description = "SEO Google Preview"


# ----------------------------------------
# 🏷️ BlogCategory Admin
# ----------------------------------------
@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "meta_title", "meta_description")


# ----------------------------------------
# 🔖 BlogTag Admin
# ----------------------------------------
@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


# ----------------------------------------
# 💬 Comment Admin
# ----------------------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "post", "approved", "created_at")
    list_filter = ("approved", "created_at")
    search_fields = ("name", "email", "content")
    readonly_fields = ("created_at",)
