# GeneInteractionApp
graph TD;
    preprocess[preprocessing]
    app[app.py]
    corr[correlations]
    data[data]
    function[functions.py]
    net[generate_network.py]

    data-->preprocess
    preprocess-->corr
    preprocess-->log
    log-- logs -->
    corr-- gene_correlation.pickle -->
    net-- processed_genes.txt -->
    function-->app
    function-->net
    function-->data
    app-->data
