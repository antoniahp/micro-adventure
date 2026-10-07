from django.contrib import admin

from microadventures.domain.models.walk import Walk


@admin.register(Walk)
class WalkAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user_id", "mood", "minutes", "weather", "swaps_used", "completed")
    list_filter = ("mood", "weather")
    search_fields = ("user_id",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    # Challenges live inside the walk; the admin shows them as text instead of a form.
    exclude = ("challenges",)
    readonly_fields = ("challenges_summary",)

    @admin.display(description="Challenges")
    def challenges_summary(self, walk):
        return "\n".join(f"[{c.status}] {c.category}: {c.text}" + (f"\n    → {c.story}" if c.story else "") for c in walk.challenges)

    @admin.display(description="Completed")
    def completed(self, walk):
        done = sum(1 for c in walk.challenges if c.is_completed)
        return f"{done}/{len(walk.challenges)}"
