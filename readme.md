# Git Contribution Analyzer

This project analyzes Git contributions of the repository it is included in. It generates detailed visualizations and statistics on contributions, such as lines of code added and removed, as well as commit frequency.

## Features
- **Git contribution analysis**: Analyze author contributions, including added and removed lines of code, and commit frequencies.
- **Interactive visualizations**: Bar graphs and Git-style heatmaps for detailed insights.
- **Dynamic HTML dashboard**: An auto-generated `index.html` provides an easy-to-navigate summary of all contributions.

## Installation and Setup

1. **Add as a Submodule**:
   Add this repository as a submodule to your project, placing it in a `.contrib` directory located at the root of your project, at the same level as the `.git` directory:
   ```bash
   git submodule add https://github.com/Multidialogo/git-squid .contrib
   ```

2. **Initialize and Update Submodules**:
   When cloning your main project, ensure the submodule is initialized and updated:
   ```bash
   git submodule update --init --recursive
   ```

3. **Pull Updates**:
   To pull the latest updates from this repository, run:
   ```bash
   git submodule update --remote
   ```


2. **Directory structure**:
   Ensure your project directory looks like this:
   ```
   project-root/
   ├── .git/
   ├── .contrib/
       ├── templates/
       ├── scripts/
       ├── plot.py
       ├── Dockerfile
       ├── docker-compose.yml
   ```

3. **Dependencies**:
    - Docker
    - Docker Compose

## Usage

### Running the Analyzer

1. Navigate to the `.contrib` directory:
   ```bash
   cd .contrib
   ```

2. Start the Docker service to analyze the Git contributions:
   ```bash
   docker compose run --rm git-log-service
   ```

### Output

After running the analyzer, the output files will be generated in the `out/latest` directory. To view the contribution summary, open the `index.html` file:
```bash
open ./out/latest/index.html
```

The HTML file contains visualizations of Git contributions for different time periods:
- Last year
- Last six months
- Last month
- Last two weeks

## Project Components

### `plot.py`
The main Python script that:
- Cleans the output directory.
- Analyzes commits from the Git repository.
- Processes contributions for each author.
- Generates visualizations (bar graphs and heatmaps).
- Outputs an `index.html` dashboard.

### `docker-compose.yml`
Defines a service (`git-log-service`) to run the Python script inside a Docker container. It ensures the required directory structure and mounts necessary volumes.

### `templates/`
Contains HTML templates to generate the `index.html` file dynamically.

## Directory Mappings in Docker

- `.git` directory of the project is mapped to `/app/.data/.git` inside the container.
- Output files are stored in the `./out` directory.
- Scripts and templates are located in `/app/scripts`.

## Contributions
Feel free to fork this repository, suggest improvements, or report issues. Contributions are always welcome!

[Contribution guideline](contributing.md)


## License
[MIT License](LICENSE)
