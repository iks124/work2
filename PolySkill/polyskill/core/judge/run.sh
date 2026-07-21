METHODS=(
    webvoyager
    webjudge_general
    webjudge_online_mind2web
)

for method in "${METHODS[@]}"; do
    mkdir -p ./judge_results/$method
    python -m judge.batch_evaluate \
        --trajectory_dir ./results/browsergym_eval/test_run/browsergym \
        --method $method \
        --limit 8 \
        --model_provider openai \
        --model_name gpt-4o \
        --output_dir ./judge_results/$method \
        --max_concurrent 8
done
