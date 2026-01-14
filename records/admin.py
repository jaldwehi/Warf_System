from django.contrib import admin
from .models import Record, KnowledgeDocument, KnowledgeChunk


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ("meeting", "created_by", "created_at")
    search_fields = ("meeting__title",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "doc_type", "visibility", "created_at")
    list_filter = ("doc_type", "visibility", "created_at")
    search_fields = ("title", "content")
    readonly_fields = ("created_at",)


@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text",)
    readonly_fields = ("created_at",)
