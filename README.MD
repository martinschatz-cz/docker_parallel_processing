# Parallel processing in Python using Docker Swarm

To approach parallel processing in Python using Docker Swarm, you can set up a distributed processing environment with Swarm managing a cluster of containers. Here’s a general guide to help you get started:

## 1. Define the Problem for Parallel Processing
Identify the task that can be split into independent chunks that can run concurrently (e.g., data processing, batch jobs, model training, etc.).
Determine if each chunk can run independently, as this will simplify container communication.

## 2. Create a Python Script for the Worker Tasks
Write a Python script that performs the individual tasks or "work units" you want to parallelize.
This worker script could, for instance, process a specific subset of data or compute a portion of a larger task.

## 3. Dockerize the Python Script
Write a Dockerfile for your Python script to create a containerized worker environment. Here’s a simplified example:
Dockerfile
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY worker_script.py .
CMD ["python", "worker_script.py"]
```
Build the Docker image:
```bash
docker build -t my_python_worker .
```

## 4. Set Up Docker Swarm
Initialize Docker Swarm on your main machine:
```bash
docker swarm init
```
Add additional nodes (if applicable) using the token provided by the Swarm manager.
	5. Deploy Services in Swarm Mode
Use Docker services to scale your workers. This command launches multiple instances of your container, each as a separate service replica:
```bash
docker service create --name my_parallel_workers --replicas 10 my_python_worker
```
You can adjust --replicas to change the number of containers (workers) running in parallel. Swarm will handle load distribution across the available nodes in the cluster.

## 6. Distribute Work Across Workers
Use a task distributor, such as a task queue, to divide and assign tasks to each worker.
A common setup is to use a message broker like RabbitMQ or Redis with Celery to manage the tasks each worker will pick up. Alternatively, you can write a custom distributor using a shared database or filesystem where each worker can pick up a task to avoid conflicts.

## 7. Monitor and Scale Services
Use Swarm’s monitoring tools or integrate with other platforms (like Portainer) to observe the workload distribution, health, and performance of each worker.
Adjust the number of replicas based on the workload by updating the service:
```
docker service scale my_parallel_workers=20
```

## 8. Handle Data Persistence and Results Collection
Ensure that results or processed data are stored in a centralized database or storage solution accessible to all workers.
You can use Docker volumes to handle shared data across containers or have each worker report results back to a database or API endpoint.

## 9. Clean Up
When processing is complete, scale down or remove the services to free resources:
```
docker service rm my_parallel_workers
```
This setup leverages Docker Swarm’s orchestration capabilities, allowing you to scale up processing across multiple nodes or a single multi-core machine. For more complex workflows, consider using orchestrators like Kubernetes or Dask if you need finer-grained control over resource allocation or specialized data flow.


# Details
Python code

```python
import os
import json
import hashlib

INPUT_DIR = "/app/data"
OUTPUT_DIR = "/app/output"
REPLICA_ID = os.getenv("REPLICA_ID")  # Use a unique ID for each replica
os.makedirs(OUTPUT_DIR, exist_ok=True)

def count_words_and_letters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    word_count = len(text.split())
    letter_count = sum(1 for char in text if char.isalpha())
    return word_count, letter_count

def process_files(input_dir):
    files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    
    # Filter files for this replica only
    assigned_files = [f for f in files if int(hashlib.md5(f.encode()).hexdigest(), 16) % REPLICA_COUNT == REPLICA_ID]

    results = {}
    for filename in assigned_files:
        file_path = os.path.join(input_dir, filename)
        word_count, letter_count = count_words_and_letters(file_path)
        results[filename] = {"words": word_count, "letters": letter_count}

    output_file = os.path.join(OUTPUT_DIR, f"results_{REPLICA_ID}.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"Replica {REPLICA_ID} processed files. Results saved to {output_file}")

if __name__ == "__main__":
    REPLICA_COUNT = int(os.getenv("REPLICA_COUNT", 1))
    REPLICA_ID = int(os.getenv("REPLICA_ID", 0))
    process_files(INPUT_DIR)
```


### Explanation
count_words_and_letters: Reads a file and counts the words and letters.
process_files: Iterates through all .txt files in the input directory, applies the counting function, and saves the results in a JSON file named results.json in the output directory.
### Dockerfile to Containerize the Worker Script
```Dockerfile
# Use an official Python image
FROM python:3.9-slim

# Set up directories
WORKDIR /app
COPY worker_script.py /app/
COPY requirements.txt /app/
RUN mkdir /app/data /app/output

# Install dependencies
RUN pip install -r requirements.txt

# Set environment variables for replica configuration
ENV INPUT_DIR=/app/data
ENV OUTPUT_DIR=/app/output
ENV REPLICA_ID=0
ENV REPLICA_COUNT=1

# Copy input files (for standalone test only - ideally, you'd use volume mounting)
COPY data /app/data

# Run the worker script
CMD ["python", "worker_script.py"]
```
### Running the Worker with Docker Swarm
Assuming you have multiple files in the input directory (data) that each worker can process, you can set up Docker Swarm to handle multiple containers running this worker script.

Build the Docker image
```bash
docker build -t my_text_worker .
```

Deploy the service in Docker Swarm
```bash
docker service create \
  --name text_processing_workers \
  --replicas 5 \
  --mount type=bind,source="$(pwd)"/data,target=/app/data \
  --mount type=bind,source="$(pwd)"/output,target=/app/output \
  my_text_worker
```

Each worker instance will process the files in parallel, outputting results to output/results.json in each container. You can later merge results from each container or use a shared storage system for centralized results collection.

This setup assumes your Docker environment can access data and output folders as mounts, enabling each worker to read inputs and write outputs accordingly.


Update your Docker service command:

```bash
docker service create \
  --name text_processing_workers \
  --replicas 5 \
  --env REPLICA_COUNT=5 \
  --env REPLICA_ID="{{.Task.Slot}}" \
  --mount type=bind,source="$(pwd)"/data,target=/app/data \
  --mount type=bind,source="$(pwd)"/output,target=/app/output \
  my_text_worker
```
In this setup:

REPLICA_COUNT is the total number of replicas.
Each replica has a unique REPLICA_ID based on its slot, enabling it to process a distinct subset of files.
This approach lets each worker process a unique subset of files without needing a message broker. Both solutions avoid duplicate work and ensure files are distributed effectively across the workers.






## Docker Test
To test this setup in Docker with just one worker, you can simplify the deployment process and run the container as a standalone instance, rather than setting up a full Swarm environment. Here’s a step-by-step guide:

### Ensure Directory Structure
Set up the following directories on your local machine to mimic the input and output directories:

```bash
mkdir -p data output
```
Add a few .txt files to the data folder to test the worker. For example:

```bash
echo "Hello world" > data/test1.txt
echo "Another test file with text" > data/test2.txt
```
2. Create the Dockerfile
Here’s a Dockerfile for building your worker image:

```Dockerfile
# Use an official Python image
FROM python:3.9-slim

# Set up directories
WORKDIR /app
COPY worker_script.py /app/
COPY requirements.txt /app/
RUN mkdir /app/data /app/output

# Install dependencies
RUN pip install -r requirements.txt

# Set environment variables for replica configuration
ENV INPUT_DIR=/app/data
ENV OUTPUT_DIR=/app/output
ENV REPLICA_ID=0
ENV REPLICA_COUNT=1

# Copy input files (for standalone test only - ideally, you'd use volume mounting)
COPY data /app/data

# Run the worker script
CMD ["python", "worker_script.py"]
```
3. Build the Docker Image
Build the Docker image using the following command:

```bash
docker build -t my_text_worker .
```
4. Run the Docker Container
Run the container with the necessary environment variables and mount the data and output directories:

```
docker run --rm --name test_worker -e REPLICA_ID=0 -e REPLICA_COUNT=1 -v "$(pwd)/data:/app/data" -v "$(pwd)/output:/app/output" my_text_worker

```

5. Verify the Output
After the container finishes processing, check the output folder on your local machine. You should see a results_0.json file containing the word and letter counts for each .txt file in the data folder.

For example, output/results_0.json might look like this:

```json
{
    "test1.txt": {
        "words": 2,
        "letters": 10
    },
    "test2.txt": {
        "words": 5,
        "letters": 18
    }
}
```
This setup confirms that the worker processes the files correctly, and you can adjust parameters if needed before scaling to multiple workers.


