from django.contrib import admin

from social_media.models import Profile, Post

# Register your models here.
admin.site.register(Profile)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "owner",
        "text",
        "created_at",
    ]
    list_filter = ["owner"]
    search_fields = ["owner"]
