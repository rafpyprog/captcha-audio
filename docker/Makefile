APP = captcha-audio
DATABASE_FILE = captcha_data.db
UPDATE-CONTAINER = captcha-update


ifeq ($(OS), Windows_NT)
    cwd = $(shell echo %CD%)
	database_path = $(cwd)\$(DATABASE_FILE)
else
	cwd = $(shell pwd)
	database_path = $(cwd)/$(DATABASE_FILE)
endif


docker-build:
	docker build -t captcha-audio:production .


docker-run:
	@docker run --rm -it -v "$(cwd)":/$(APP) --name work $(APP):production /bin/bash

docker-run-jupyter:
	docker run --rm -p 8888:8888 -v "$(cwd)"/app:/$(APP) $(APP):production /bin/bash -c "jupyter notebook --ip=0.0.0.0 --allow-root --no-browser"

docker-update-py:
	@echo - Launching update container: $(UPDATE-CONTAINER)
	@docker run --name $(UPDATE-CONTAINER) -d -it $(APP):production
	docker exec $(UPDATE-CONTAINER) mkdir /newfiles
	docker cp . $(UPDATE-CONTAINER):/newfiles
	docker exec $(UPDATE-CONTAINER) /bin/sh -c "cp /newfiles/*.py /captcha-audio"
	docker exec $(UPDATE-CONTAINER) rm -rf /newfiles
	docker stop $(UPDATE-CONTAINER)
	@echo - Commiting changes to $(APP):production
	@docker commit $(UPDATE-CONTAINER) $(APP):production
	@echo - Removing container $(UPDATE-CONTAINER)
	@docker rm $(UPDATE-CONTAINER)
	@echo - Image updated!


rm-update:
	docker stop $(UPDATE-CONTAINER)
	docker rm $(UPDATE-CONTAINER)


alpine:
	@docker run --rm -it -v "$(cwd)":/$(APP) --name work $(APP):production python3 $(APP)/test_selenium.py

alpine-sh:
	@docker run --rm -it -v "$(cwd)":/$(APP) --name work $(APP):production sh
