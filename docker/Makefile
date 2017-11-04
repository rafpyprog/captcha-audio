APP = captcha-audio
UPDATE-CONTAINER = captcha-update


ifeq ($(OS), Windows_NT)
    cwd = $(shell echo %CD%)
else
	cwd = $(shell pwd)
endif


docker-build:
	docker build -t captcha-audio:production .


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


jupyter:
	docker run --rm -it -p 8888:8888 -v "$(cwd)/app":/$(APP) $(APP):production jupyter notebook --ip=0.0.0.0 --allow-root --no-browser


getdata:
	@docker run --rm -it -v "$(cwd)/app/":/$(APP) --name getdata $(APP):production python3 getdata.py


alpine-sh:
	@docker run --rm -it -v "$(cwd)/app/":/$(APP) --name work $(APP):production sh
