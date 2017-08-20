tox -e python$TRAVIS_PYTHON_VERSION
coverage xml -i || true
sed -i 's/filename="/filename=".\//g' coverage.xml || true

if [ "$TRAVIS_PULL_REQUEST" ]
then
	echo "sonar-scanner for PR"
	docker run -v `pwd`:/data rcommande/sonar-scanner -Dsonar.analysis.mode=preview -Dsonar.github.pullRequest=$PULL_REQUEST_ID -Dsonar.github.repository=rcommande/papaye -Dsonar.github.oauth=$GITHUB_ACCESS_TOKEN -Dsonar.host.url=https://sonarcloud.io -Dsonar.login=$SONAR_TOKEN -Dsonar.organization=rcommande
else
	echo "sonar-scanner"
	docker run -v `pwd`:/data rcommande/sonar-scanner -Dsonar.host.url=https://sonarcloud.io -Dsonar.login=$SONAR_TOKEN -Dsonar.organization=rcommande -Dsonar.sources=/data/. -Dsonar.projectKey=papaye
fi
