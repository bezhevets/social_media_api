from django.contrib import admin

from social_media.models import (
    Profile,
    Post,
    Comment,
    Like
)

# Register your models here.
admin.site.register(Profile)
admin.site.register(Like)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "owner",
        "text",
        "created_at",
    ]
    list_filter = ["owner"]
    search_fields = ["owner"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "get_owner_full_name",
        "post",
        "text",
        "created_at",
    ]
    search_fields = ["owner__last_name"]

    def get_owner_full_name(self, obj):
        return obj.owner.full_name if obj.owner else None

    get_owner_full_name.short_description = "Owner Full Name"
