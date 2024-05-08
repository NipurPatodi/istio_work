FROM rayproject/ray:2.9.0
COPY test_dag /serve_app/ray_observe_exp
WORKDIR /serve_app/ray_observe_exp