ctx_name="$1"
shift
nohup python3 -u discretion.py -m en_core_web_sm -cfg configs/*yaml -ctx $ctx_name -p 8080 "$@" &> stdout.log &
echo "$!" | tee "$PWD/pid"
