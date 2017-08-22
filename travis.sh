SONAR_TOKEN=$1
GITHUB_TOKEN=$2
PULL_REQUEST_ID=$3
JOB_NUMBER=$4
TASK_NUMBER=$(echo $JOB_NUMBER | cut -d '.' -f2)

tox -e python$TRAVIS_PYTHON_VERSION
coverage xml -i || true
sed -i 's/filename="/filename=".\//g' coverage.xml || true 

if [ "$TASK_NUMBER" == 1 ]
then
	if [ "$PULL_REQUEST_ID" == 'false' ]
	then
		docker run -v `pwd`:/data rcommande/sonar-scanner \
			-Dsonar.host.url=https://sonarcloud.io \
			-Dsonar.login=$SONAR_TOKEN \
			-Dsonar.organization=rcommande \
			-Dsonar.sources=/data/. \
			-Dsonar.projectKey=papaye
	else
		docker run -v `pwd`:/data rcommande/sonar-scanner \
			-Dsonar.analysis.mode=preview \
			-Dsonar.github.pullRequest=$PULL_REQUEST_ID \
			-Dsonar.github.repository=rcommande/papaye \
			-Dsonar.github.oauth=$GITHUB_TOKEN \
			-Dsonar.host.url=https://sonarcloud.io \
			-Dsonar.login=$SONAR_TOKEN \
			-Dsonar.organization=rcommande \
			-Dsonar.sources=/data/. \
			-Dsonar.projectKey=papaye
	fi
fi
