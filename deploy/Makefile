mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
cur_makefile_path := $(dir $(mkfile_path))
build:
	docker build $(cur_makefile_path)\.. -f $(cur_makefile_path)\Dockerfile -t multi-benchmark --progress=plain

run:
	docker run --name multi-benchmark --restart always -p 5000:5000 -v $(cur_makefile_path)/..:/work/ -d etherealo/multi-benchmark