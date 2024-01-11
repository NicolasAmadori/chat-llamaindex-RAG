# Insufficient number of arguments
if [ $# -lt 1 ]; then
    echo "Usage: ./run_docker.sh [run|exec|build|stop|remove]"
    exit 1
fi

case $1 in
    run)
        # Run the docker container
        docker run -v ./:/src/ --rm --gpus device=$CUDA_VISIBLE_DEVICES -d -it -p 37331:37331 -p 37333:37333 -p 19530:19530 --name clvz-llamaindex-container clvz-llamaindex
        ;;
    exec)
        # Execute the models inside the docker container
        docker exec -it clvz-llamaindex-container bash      
        ;;
    build)
        # Build the docker
        docker build ./ -t clvz-llamaindex
        ;;
    stop)
        # Stop the docker container
        docker stop clvz-llamaindex-container
        ;;
    remove)
        # Remove the docker container
        docker stop clvz-llamaindex-container &&
        docker remove clvz-llamaindex-container
        ;;
    *)
        # Invalid argument
        echo "Invalid argument"
        ;;
esac
