rule rapidnj_tree:
    input:
        concat_alignments_dir_path / stockholm_dna_filename,
    output:
        rapidnj_dir_path / rapidnj_tree,
    params:
        config["rapidnj_params"],
    log:
        std=log_dir_path / "rapidnj_tree.log",
        cluster_log=cluster_log_dir_path / "rapidnj_tree.cluster.log",
        cluster_err=cluster_log_dir_path / "rapidnj_tree.cluster.err",
    benchmark:
        benchmark_dir_path / "rapidnj_tree.benchmark.txt"
    conda:
        config["conda"]["buscoclade_main"]["name"] if config["use_existing_envs"] else ("../../%s" % config["conda"]["buscoclade_main"]["yaml"])
    resources:
        queue=config["rapidnj_queue"],
        cpus=config["rapidnj_threads"],
        time=config["rapidnj_time"],
        mem_mb=config["rapidnj_mem_mb"],
    threads: config["rapidnj_threads"]
    shell:
        " rapidnj -i sth -c {threads} {params} {input} > {output} 2> {log.std}; "
