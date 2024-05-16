from enum import Enum

# Choices for Recipe model
RECIPE_STATUS_CHOICES = [
  ("DRAFT", "draft"),
  ("PUBLISHED", "published")
]

class VoteType(Enum):
  UP_VOTED   = "UP_VOTED"
  DOWN_VOTED = "DOWN_VOTED"