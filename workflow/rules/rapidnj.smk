rule rapidnj_tree:
    input:
        archive=concat_alignments_dir_path / "concat_fasta.tar.gz",
    output:
        tree=rapidnj_dir_path / rapidnj_tree,
    params:
        config["rapidnj_params"],
    log:
        std=log_dir_path / "rapidnj_tree.log",
        cluster_log=cluster_log_dir_path / "rapidnj_tree.cluster.log",
        cluster_err=cluster_log_dir_path / "rapidnj_tree.cluster.err",
    benchmark:
        benchmark_dir_path / "rapidnj_tree.benchmark.txt",
    conda:
        "../../%s" % config["conda_config"],
    resources:
        queue=config["rapidnj_queue"],
        cpus=config["rapidnj_threads"],
        time=config["rapidnj_time"],
        mem_mb=config["rapidnj_mem_mb"],
    threads: config["rapidnj_threads"],
    shell:
        """
        tar -xOf {input.archive} {wildcards.stockholm_dna_filename} > temp.sth &&
        rapidnj -i sth -c {threads} {params} temp.sth > {output.tree} 2> {log.std} &&
        rm temp.sth
        """
