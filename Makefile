docker-build:
	docker build -t captcha-audio:production .


docker-run:
	docker run -it captcha-audio:production sh


UPDATE-CONTAINER=captcha-update
docker-update-py:
	docker run --name $(UPDATE-CONTAINER) -d -it captcha-audio:production
	docker exec $(UPDATE-CONTAINER) mkdir /newfiles
	docker cp . $(UPDATE-CONTAINER):/newfiles
	docker exec $(UPDATE-CONTAINER) /bin/sh -c "cp /newfiles/*.py /captcha-audio"
	docker exec $(UPDATE-CONTAINER) rm -rf /newfiles
	docker exec $(UPDATE-CONTAINER) ls /captcha-audio
	docker stop $(UPDATE-CONTAINER)
	docker commit $(UPDATE-CONTAINER) captcha-audio:production
	docker rm $(UPDATE-CONTAINER)

rm-update:
	docker stop $(UPDATE-CONTAINER)
	docker rm $(UPDATE-CONTAINER)
