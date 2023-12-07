# GeneInteractionApp
-- IN PROGRESS --
The Gene Interaction App is an interactive tool designed to explore genetic interactions post CRISPR knockout, allowing users to investigate how the absence of specific genes affects other genes within cancer cell lines. Based on the DepMap project, this application enables users to select and analyze two genes, observing the correlations between these genes and identifying shared correlations post-gene knockout.

## Usage
1. **Clone the Repository:**
    ```bash
    git clone https://github.com/ntmaseras/GeneInteractionApp.git
    ```

2. **Run the Application:**
    - For testing, only some genes available.
    - Install necessary dependencies (provided environment.yml).
    - Execute the main application file `app.py`.
    ```bash
     python3 app.py
    ```
```mermaid
graph TD;
    genes[data/genes.txt]
    log1[log/execution.log]
    achilles[data/achilles_generated.csv]
    mapa[data/map_generated.csv]
    log2[log/completed_genes.txt]
    corrsFiles[correlations/correlations_GENE*.csv]
    corrPy[correlations.py]
    corrSh[correlations_batch.sh]
    function[functions.py]
    net[generate_network.py]
    app[app.py]

    style genes fill:#7cb5ec,stroke:#333,stroke-width:2px;
    style log1 fill:#7cb5ec,stroke:#333,stroke-width:2px;
    style achilles fill:#7cb5ec,stroke:#333,stroke-width:2px;
    style mapa fill:#7cb5ec,stroke:#333,stroke-width:2px;
    style log2 fill:#7cb5ec,stroke:#333,stroke-width:2px;
    style corrsFiles fill:#7cb5ec,stroke:#333,stroke-width:2px;

    genes-->corrSh
    log1-->corrSh
    log2-->corrSh
    achilles-->corrPy
    mapa-->function
    corrSh-->corrPy
    corrPy-->corrsFiles
    corrsFiles-->app
    genes-->app
    corrsFiles-->function
    function-->app
    genes-->net
    net-- network/gene_correlation.pickle -->app
    corrsFiles-->net

```
## Acknowledgements

The Gene Interaction App acknowledges the following projects, resources, and individuals for their contributions:

- **DepMap Project:** Acknowledgment to the DepMap project for providing the essential datasets and resources for correlation analysis.
- **Contributors:** Appreciation to all contributors who have helped improve and develop this app.

