import os
import git
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta

# Directories
GIT_DIR = '../.data/.git'  # Path to your .git directory
OUTPUT_DIR = '../out/latest'  # Path to your output directory
TEMPLATE_PATH = 'templates/plot/index.tpl.html'  # Path to the main HTML template
TAB_CONTENT_TEMPLATE_PATH = 'templates/plot/tabs.tpl.html'  # Path to the tab content template
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Time periods
TIME_PERIODS = {
    "last_year": 365,
    "last_six_months": 180,
    "last_month": 30,
    "last_two_weeks": 14,
}

# Function to clean the output directory
def clean_output_dir(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)  # Remove the directory
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
    else:
        os.makedirs(directory, exist_ok=True)
    print(f"Cleaned directory: {directory}")

# Function to fetch commits for a time period
def get_commits(repo, days_back):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=days_back)
    return [
        commit for commit in repo.iter_commits()
        if start_date <= commit.committed_datetime.date() <= end_date
    ]

# Function to process commits into author contributions
def process_commits(commits):
    author_contributions = defaultdict(lambda: {"added": 0, "removed": 0, "commit_dates": []})
    for commit in commits:
        email = commit.author.email
        try:
            diff = commit.stats
            author_contributions[email]["added"] += diff.total["insertions"]
            author_contributions[email]["removed"] += diff.total["deletions"]
            commit_date = commit.committed_datetime.date()
            author_contributions[email]["commit_dates"].append(commit_date)
        except Exception as e:
            print(f"Error processing commit {commit.hexsha}: {e}")
    return author_contributions

def generate_git_contribution_graph(commit_dates, start_date, days_in_period, ax):
    """
    Generates a Git-style contribution graph where each day is represented by a square.
    This function replaces the previous 'contribution graph' functionality.

    Parameters:
    - commit_dates (list): List of commit dates as datetime objects.
    - start_date (datetime.date): The start date of the period.
    - days_in_period (int): Total number of days in the period.
    - ax (matplotlib.axes.Axes): The axis to plot the graph on.

    Returns:
    - tick_labels (list): The labels for the ticks on the x-axis.
    - cax (matplotlib.colorbar.Colorbar): The colorbar object associated with the heatmap.
    """
    # Count the commits for each day
    commit_counts = defaultdict(int)
    for date in commit_dates:
        commit_counts[date] += 1

    # Create a grid for the GitHub-style contribution graph (1 column per day)
    date_range = [start_date + timedelta(days=i) for i in range(days_in_period)]
    grid = np.zeros((days_in_period, 1))  # One column for each day
    for i, date in enumerate(date_range):
        grid[i, 0] = commit_counts.get(date, 0)

    # Plot heatmap for the contribution graph (each square represents a day)
    cax = ax.imshow(grid.T, cmap='YlGnBu', aspect='auto', interpolation='nearest')  # Transpose grid for vertical

    # Set the x-ticks to represent weeks or intervals within the period
    num_ticks = 7  # Number of ticks you want for the graph
    tick_positions = np.linspace(0, days_in_period - 1, num_ticks, dtype=int)
    tick_labels = [(start_date + timedelta(days=int(tick_position))).strftime('%b %d') for tick_position in tick_positions]

    ax.set_xticks(tick_positions)  # Set the positions for ticks
    ax.set_xticklabels(tick_labels)  # Set the labels for those ticks
    ax.set_yticks([0])
    ax.set_yticklabels(["Commits"])

    # Return the tick positions and labels for future use if needed
    return tick_labels, cax

def save_graphs(author_contributions, period_name):
    # Sort authors by total moved lines (added + removed)
    sorted_contributions = sorted(
        author_contributions.items(),
        key=lambda x: x[1]["added"] + x[1]["removed"],
        reverse=True
    )
    graph_paths = []
    for author, stats in sorted_contributions:
        if stats["added"] == 0 and stats["removed"] == 0:
            continue

        # Create a figure for the SVG with modified height ratios
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 12), gridspec_kw={'height_ratios': [2, 0.5]})

        # Bar graph for added/removed lines (Top part of the combined graph)
        ax1.bar(["Added", "Removed"], [stats["added"], stats["removed"]], color=["green", "red"])
        ax1.set_title(f"{author} - {period_name}\nTotal: {stats['added']} added, {stats['removed']} removed",
                      fontsize=14, weight="bold")
        ax1.set_ylabel("Lines of Code", fontsize=12)
        ax1.set_xlabel("Change Type", fontsize=12)

        # Generate commit frequency graph (Bottom part of the combined graph)
        commit_dates = stats["commit_dates"]
        days_in_period = TIME_PERIODS[period_name]  # Use the actual period length
        start_date = datetime.today().date() - timedelta(days=days_in_period)

        # Call the function to generate the new contribution graph (Git-style grid heatmap)
        tick_labels, cax = generate_git_contribution_graph(commit_dates, start_date, days_in_period, ax2)

        # Add a color bar to the contribution graph
        fig.colorbar(cax, ax=ax2, label="Commits")

        # Adjust layout and save as SVG
        plt.tight_layout()
        graph_filename = f"{author.replace('@', '_')}_{period_name.replace(' ', '_')}.svg"
        graph_path = os.path.join(OUTPUT_DIR, graph_filename)
        plt.savefig(graph_path, format='svg', bbox_inches="tight")  # Save as SVG format
        plt.close()
        graph_paths.append((author, graph_filename))
        print(f"Graph saved: {graph_path}")
    return graph_paths

# Function to generate the index.html file using templates
def generate_index_html(graph_data):
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template file not found at {TEMPLATE_PATH}")

    if not os.path.exists(TAB_CONTENT_TEMPLATE_PATH):
        raise FileNotFoundError(f"Tab content template file not found at {TAB_CONTENT_TEMPLATE_PATH}")

    # Read the main template
    with open(TEMPLATE_PATH, "r") as template_file:
        html_content = template_file.read()

    # Read the tab content template
    with open(TAB_CONTENT_TEMPLATE_PATH, "r") as tab_content_template_file:
        tab_content_template = tab_content_template_file.read()

    # Generate the select options and tab content dynamically
    select_options = ""
    tab_contents_html = ""
    for period_name, graphs in graph_data.items():
        select_options += f'<option value="{period_name}">{period_name.replace("_", " ").title()}</option>\n'

        graph_items = ""
        for author, graph_filename in graphs:
            graph_items += f'<div class="contributor-item"><img src="{graph_filename}" alt="{author}"><p>{author}</p></div>\n'

        tab_content_html = tab_content_template
        tab_content_html = tab_content_html.replace("{{TAB_ID}}", period_name)
        tab_content_html = tab_content_html.replace("{{PERIOD_NAME}}", period_name.replace("_", " ").title())
        tab_content_html = tab_content_html.replace("{{GRAPH_ITEMS}}", graph_items)

        tab_contents_html += tab_content_html

    # Replace placeholders in the main template
    html_content = html_content.replace("<!-- TABS_PLACEHOLDER -->", select_options)
    html_content = html_content.replace("<!-- TAB_CONTENT_PLACEHOLDER -->", tab_contents_html)

    # Save the updated HTML
    html_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(html_path, "w") as output_file:
        output_file.write(html_content)

    print(f"Index HTML generated: {html_path}")

# Main function
def main():
    clean_output_dir(OUTPUT_DIR)  # Clean the output directory at the start
    repo = git.Repo(GIT_DIR)
    graph_data = {}

    for period_name, days_back in TIME_PERIODS.items():
        print(f"Processing period: {period_name}")
        commits = get_commits(repo, days_back)
        print(f"Found {len(commits)} commits for {period_name}")
        author_contributions = process_commits(commits)
        graphs = save_graphs(author_contributions, period_name)
        graph_data[period_name] = graphs

    generate_index_html(graph_data)

if __name__ == "__main__":
    main()
