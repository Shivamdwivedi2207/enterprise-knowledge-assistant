from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class CreateCalendarEventRequest(BaseModel):
    """
    Request body used to create a Google Calendar event.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the calendar event.",
        examples=[
            "Enterprise Knowledge Assistant Meeting"
        ],
    )

    start_time: datetime = Field(
        ...,
        description=(
            "Event start time in ISO-8601 format, "
            "including the timezone offset."
        ),
        examples=[
            "2026-08-07T17:00:00+05:30"
        ],
    )

    end_time: datetime = Field(
        ...,
        description=(
            "Event end time in ISO-8601 format, "
            "including the timezone offset."
        ),
        examples=[
            "2026-08-07T18:00:00+05:30"
        ],
    )

    description: str = Field(
        default="",
        max_length=5000,
        description="Optional event description.",
        examples=[
            (
                "Discuss the Enterprise Knowledge Assistant "
                "development progress."
            )
        ],
    )

    location: str = Field(
        default="",
        max_length=500,
        description="Optional event location.",
        examples=[
            "Seminar Hall 2"
        ],
    )

    @model_validator(mode="after")
    def validate_event_times(
        self,
    ) -> "CreateCalendarEventRequest":
        """
        Ensure the event ends after it starts.
        """

        if self.end_time <= self.start_time:
            raise ValueError(
                "The event end time must be later "
                "than the start time."
            )

        return self


class CreateCalendarEventResponse(BaseModel):
    """
    Response returned after the n8n calendar
    workflow executes.
    """

    success: bool

    message: str

    event_id: str | None = None

    event_link: str | None = None