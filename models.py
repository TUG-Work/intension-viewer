"""
In/Tension Domain Model

Object model using controlled vocabulary from the TUG specification.

TERMINOLOGY (from spec):
- Project: Container that holds a set of continuums
- Aim: A strategic goal or position desirable to the organization
- Tension: A set of two aims
- Continuum: Visual presentation of a tension on a spectrum
- Continuum Set: Collection of all continuums in a project
- Vote: Participant's expression of how a continuum should be balanced
- Baseline: First round (how organization IS balancing)
- Comparison: Second round (how organization SHOULD balance)
- Consent Point: Average of votes, or facilitator-adjusted value
- Participant: Individual who votes on continuums
- Report: Summary of continuum set with baseline and comparison votes
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from statistics import mean


class VotingRound(Enum):
    """The two rounds of voting in a workshop."""
    BASELINE = "baseline"      # How we ARE balancing
    COMPARISON = "comparison"  # How we SHOULD balance


@dataclass
class Aim:
    """
    A strategic goal or position desirable to the organization.
    
    Each Tension has exactly two Aims, representing opposite ends
    of a strategic spectrum.
    """
    label: str
    description: Optional[str] = None


@dataclass
class Participant:
    """
    An individual from the organization who votes on continuums.
    
    Participants don't need accounts - they're identified by
    a display name and hashed email for the workshop.
    """
    id: str
    display_name: str
    color: Optional[str] = None  # For visual distinction in results


@dataclass
class Vote:
    """
    One participant's expression of how a continuum should be balanced.
    
    A Vote captures both CONTEXT and FOCUS:
    
    CONTEXT (where this vote lives):
    - participant: Who cast this vote
    - tension_id: Which continuum this vote is for
    - round: Which voting round (baseline or comparison)
    - project_id: Which project/workshop this belongs to
    
    FOCUS (the actual expression):
    - value: Position on the scale (integer, typically 0-10)
      - Lower values = lean toward left aim
      - Higher values = lean toward right aim
    
    LIFECYCLE:
    - submitted_at: When the vote was first submitted
    - updated_at: When the vote was last changed (if edited)
    
    Per spec: "Participants must be able to return to continuums and edit 
    votes when this function has been enabled by the facilitator."
    """
    # Context
    participant: Participant
    tension_id: str           # Which continuum this vote is for
    round: VotingRound        # Baseline or Comparison
    value: int                # Position on the scale (0-10) - FOCUS
    
    # Optional context
    project_id: Optional[str] = None  # Parent project (for cross-reference)
    
    # Lifecycle
    submitted_at: Optional[str] = None  # ISO timestamp
    updated_at: Optional[str] = None    # ISO timestamp (if edited)
    
    @property
    def is_edited(self) -> bool:
        """True if this vote was changed after initial submission."""
        return self.updated_at is not None and self.updated_at != self.submitted_at


@dataclass
class ConsentPoint:
    """
    The agreed-upon position for a continuum after discussion.
    
    Defaults to the average of all votes, but can be manually
    adjusted by the facilitator to capture group consensus.
    """
    round: VotingRound
    value: float
    is_manual: bool = False  # True if facilitator adjusted it
    
    @classmethod
    def from_votes(cls, votes: List[Vote], round: VotingRound) -> Optional['ConsentPoint']:
        """Calculate consent point from vote average."""
        round_votes = [v for v in votes if v.round == round]
        if not round_votes:
            return None
        avg = mean(v.value for v in round_votes)
        return cls(round=round, value=avg, is_manual=False)


@dataclass
class Continuum:
    """
    The visual presentation of a tension as a spectrum.
    
    A Continuum displays:
    - Two aims at opposite ends
    - Individual votes as stacked markers
    - Consent point (average or adjusted) as a circle
    - Optional comparison round below the line
    """
    tension: 'Tension'
    scale_min: int = 0
    scale_max: int = 10
    
    @property
    def scale_positions(self) -> int:
        """Number of discrete positions on the scale."""
        return self.scale_max - self.scale_min + 1


@dataclass
class Tension:
    """
    A set of two aims that must be balanced.
    
    The core concept in In/Tension modeling: two equally desirable
    goals that draw from the same resources, requiring the organization
    to choose how to balance them.
    """
    name: str
    left_aim: Aim   # Position 0 on the scale
    right_aim: Aim  # Position 10 on the scale
    votes: List[Vote] = field(default_factory=list)
    consent_points: List[ConsentPoint] = field(default_factory=list)
    is_hidden: bool = False  # Hidden from presentation/voting
    order: int = 0  # Display order in project
    
    def add_vote(self, vote: Vote) -> None:
        """
        Record a vote on this tension.
        
        Automatically sets the vote's tension_id if not already set.
        """
        if not vote.tension_id:
            vote.tension_id = self.name  # Use name as ID for now
        self.votes.append(vote)
    
    def get_votes(self, round: VotingRound) -> List[Vote]:
        """Get all votes for a specific round."""
        return [v for v in self.votes if v.round == round]
    
    def get_consent_point(self, round: VotingRound) -> Optional[ConsentPoint]:
        """
        Get the consent point for a round.
        Returns manual override if set, otherwise calculates from votes.
        """
        # Check for manual override
        for cp in self.consent_points:
            if cp.round == round and cp.is_manual:
                return cp
        # Calculate from votes
        return ConsentPoint.from_votes(self.votes, round)
    
    def set_consent_point(self, round: VotingRound, value: float) -> None:
        """Manually set the consent point (facilitator override)."""
        # Remove existing manual point for this round
        self.consent_points = [
            cp for cp in self.consent_points 
            if not (cp.round == round and cp.is_manual)
        ]
        self.consent_points.append(
            ConsentPoint(round=round, value=value, is_manual=True)
        )
    
    def get_movement(self) -> Optional[float]:
        """
        Calculate movement from baseline to comparison.
        
        Positive = moved toward right aim
        Negative = moved toward left aim
        """
        baseline = self.get_consent_point(VotingRound.BASELINE)
        comparison = self.get_consent_point(VotingRound.COMPARISON)
        if baseline is None or comparison is None:
            return None
        return comparison.value - baseline.value
    
    def as_continuum(self) -> Continuum:
        """Get the visual representation of this tension."""
        return Continuum(tension=self)


@dataclass
class Project:
    """
    The container that holds a set of continuums (tensions).
    
    A Project represents one In/Tension modeling engagement,
    containing all the tensions to be worked through with participants.
    """
    id: str
    name: str
    tensions: List[Tension] = field(default_factory=list)
    participants: List[Participant] = field(default_factory=list)
    baseline_code: Optional[str] = None   # Access code for baseline voting
    comparison_code: Optional[str] = None  # Access code for comparison voting
    
    def add_tension(self, tension: Tension) -> None:
        """Add a tension to the project."""
        tension.order = len(self.tensions)
        self.tensions.append(tension)
    
    def add_participant(self, participant: Participant) -> None:
        """Add a participant to the project."""
        self.participants.append(participant)
    
    def get_visible_tensions(self) -> List[Tension]:
        """Get tensions that are not hidden, in display order."""
        return sorted(
            [t for t in self.tensions if not t.is_hidden],
            key=lambda t: t.order
        )
    
    @property
    def continuum_set(self) -> List[Continuum]:
        """The collection of all continuums in this project."""
        return [t.as_continuum() for t in self.get_visible_tensions()]


# Type alias for clarity
ContinuumSet = List[Continuum]


class SessionStatus(Enum):
    """Status of a voting session."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"


class SubmissionMode(Enum):
    """How votes are submitted."""
    ONE_BY_ONE = "one_by_one"    # Submit each vote individually
    BATCH = "batch"              # Vote all, then submit together


@dataclass
class VotingSession:
    """
    A participant's voting session within a workshop.
    
    Manages the flow of voting on a sequence of tensions,
    tracking progress and pending votes until submission.
    """
    session_id: str
    project: Project
    round: VotingRound
    participant: Participant
    submission_mode: SubmissionMode = SubmissionMode.BATCH
    
    # State
    current_index: int = 0
    pending_votes: dict = field(default_factory=dict)  # tension_id -> value
    status: SessionStatus = SessionStatus.NOT_STARTED
    
    @property
    def tensions(self) -> List[Tension]:
        """Get the ordered list of tensions to vote on."""
        return self.project.get_visible_tensions()
    
    @property
    def current_tension(self) -> Optional[Tension]:
        """Get the currently active tension."""
        tensions = self.tensions
        if 0 <= self.current_index < len(tensions):
            return tensions[self.current_index]
        return None
    
    @property
    def progress(self) -> tuple:
        """Return (current, total) for progress display."""
        return (self.current_index + 1, len(self.tensions))
    
    @property
    def is_complete(self) -> bool:
        """True if all tensions have been voted on."""
        return len(self.pending_votes) == len(self.tensions)
    
    def start(self) -> None:
        """Begin the voting session."""
        self.status = SessionStatus.IN_PROGRESS
        self.current_index = 0
    
    def cast_vote(self, value: int) -> None:
        """
        Record a vote for the current tension.
        
        Value should be 0-10 (11 positions).
        """
        if self.current_tension is None:
            raise ValueError("No current tension")
        if not 0 <= value <= 10:
            raise ValueError(f"Vote value must be 0-10, got {value}")
        
        tension_id = self.current_tension.name
        self.pending_votes[tension_id] = value
        
        # In one-by-one mode, could trigger immediate submission here
    
    def get_vote(self, tension_id: str) -> Optional[int]:
        """Get the pending vote for a tension, if any."""
        return self.pending_votes.get(tension_id)
    
    def next_tension(self) -> bool:
        """Move to next tension. Returns False if at end."""
        if self.current_index < len(self.tensions) - 1:
            self.current_index += 1
            return True
        return False
    
    def previous_tension(self) -> bool:
        """Move to previous tension. Returns False if at start."""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False
    
    def go_to_tension(self, index: int) -> bool:
        """Jump to a specific tension by index."""
        if 0 <= index < len(self.tensions):
            self.current_index = index
            return True
        return False
    
    def submit(self) -> List[Vote]:
        """
        Submit all pending votes.
        
        Returns the list of Vote objects created.
        """
        if self.status == SessionStatus.SUBMITTED:
            raise ValueError("Session already submitted")
        
        votes = []
        timestamp = None  # Would be datetime.now().isoformat() in real use
        
        for tension in self.tensions:
            value = self.pending_votes.get(tension.name)
            if value is not None:
                vote = Vote(
                    participant=self.participant,
                    tension_id=tension.name,
                    round=self.round,
                    value=value,
                    project_id=self.project.id,
                    submitted_at=timestamp
                )
                tension.add_vote(vote)
                votes.append(vote)
        
        self.status = SessionStatus.SUBMITTED
        return votes
