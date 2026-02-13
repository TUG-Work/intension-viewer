"""
In/Tension Viewer Application

Loads session data and renders visualizations.
"""

from models import Project, Tension, Aim, Participant, Vote, VotingRound
from views import ProjectView


def load_march_2025_session() -> Project:
    """
    Load the real March 2025 workshop session data.
    
    This demonstrates how to build a Project from raw data.
    """
    
    # Create the project
    project = Project(
        id="march-2025",
        name="In/Tension Session Results"
    )
    
    # Add participants
    participants = [
        Participant(id="stratton", display_name="Stratton Glaze"),
        Participant(id="emily", display_name="Emily"),
        Participant(id="klyn", display_name="Klyn"),
        Participant(id="andrew", display_name="Andrew"),
        Participant(id="bob", display_name="Bob"),
        Participant(id="dan", display_name="Dan Heck"),
    ]
    for p in participants:
        project.add_participant(p)
    
    # Define tensions with their aims
    tensions_data = [
        {
            "name": "Quality vs Quantity of Outputs",
            "left": Aim("Quality", "Focus on excellence"),
            "right": Aim("Quantity", "Focus on volume"),
            "baseline_votes": [0, 1, 1, 4, 3, 5],
        },
        {
            "name": "Data Tracking vs Privacy",
            "left": Aim("Comprehensive Tracking"),
            "right": Aim("Privacy by Design"),
            "baseline_votes": [5, 9, 5, 9, 2, 5],
        },
        {
            "name": "Oversight vs Personalization",
            "left": Aim("Centralized Oversight"),
            "right": Aim("Personalization"),
            "baseline_votes": [1, 2, 8, 3, 5, 6],
        },
        {
            "name": "Outputs vs Experiences",
            "left": Aim("Good AI Outputs"),
            "right": Aim("Good Workflow Experiences"),
            "baseline_votes": [1, 3, 9, 3, 3, 4],
        },
        {
            "name": "Back Office vs Front Office",
            "left": Aim("Back Office"),
            "right": Aim("Front Office"),
            "baseline_votes": [0, 0, 2, 0, 1, 1],
        },
        {
            "name": "Understanding vs Privacy",
            "left": Aim("Understanding"),
            "right": Aim("Privacy"),
            "baseline_votes": [5, 7, 7, 6, 7, 3],
        },
        {
            "name": "Responsive vs Inclusive Governance",
            "left": Aim("Quick Response"),
            "right": Aim("Inclusive Process"),
            "baseline_votes": [2, 3, 7, 6, 4, 4],
        },
    ]
    
    # Build tensions and votes
    for data in tensions_data:
        tension = Tension(
            name=data["name"],
            left_aim=data["left"],
            right_aim=data["right"]
        )
        
        # Add baseline votes
        for participant, value in zip(participants, data["baseline_votes"]):
            tension.add_vote(Vote(
                participant=participant,
                tension_id=data["name"],
                round=VotingRound.BASELINE,
                value=value,
                project_id=project.id,
                submitted_at="2025-03-28T12:00:00Z"  # From original session
            ))
        
        project.add_tension(tension)
    
    return project


def main():
    """Generate the visualization."""
    
    # Load data
    project = load_march_2025_session()
    
    # Render to HTML
    view = ProjectView(project, show_comparison=False)
    html = view.render()
    
    # Write output
    with open("public/index.html", "w") as f:
        f.write(html)
    
    # Report
    print(f"Generated public/index.html")
    print(f"  Project: {project.name}")
    print(f"  Participants: {len(project.participants)}")
    print(f"  Tensions: {len(project.tensions)}")
    
    # Show consent points
    print(f"\nConsent Points (Baseline):")
    for tension in project.get_visible_tensions():
        cp = tension.get_consent_point(VotingRound.BASELINE)
        if cp:
            print(f"  {tension.name}: {cp.value:.1f}")


if __name__ == "__main__":
    main()
