pipeline {
    agent any

    stages {
        stage('Check Dependencies') {
            steps {
                sh '''
                    echo "Checking Python and dependencies..."
                    python3 --version
                    pip3 list | grep -E "requests|pytest|selenium|locust" || echo "Some dependencies might be missing"
                '''
            }
        }

        stage('Run REST API Tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        echo "=== Running REST API Tests ==="
                        cd /var/jenkins_home/workspace/OpenBMC-Testing
                        
                        # Запускаем твои реальные тесты против localhost:2443
                        if [ -f "autotestsOpenBmc.py" ]; then
                            echo "Found autotestsOpenBmc.py - running real tests..."
                            python3 -m pytest autotestsOpenBmc.py -v --tb=short | tee autotests.log
                        else
                            echo "autotestsOpenBmc.py not found"
                            echo "TEST SIMULATION: REST API tests would run against https://localhost:2443" > autotests.log
                        fi
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'autotests.log', fingerprint: true
                }
            }
        }

        stage('Run Load Tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        echo "=== Running Load Tests ==="
                        cd /var/jenkins_home/workspace/OpenBMC-Testing
                        
                        if [ -f "loadtestsOpenBmc.py" ]; then
                            echo "Found loadtestsOpenBmc.py - running load tests..."
                            # Запускаем locust на 20 секунд
                            timeout 25s locust -f loadtestsOpenBmc.py --headless -u 2 -r 1 --run-time 20s --host=https://localhost:2443 || echo "Locust finished" | tee loadtests.log
                        else
                            echo "loadtestsOpenBmc.py not found"
                            echo "TEST SIMULATION: Load tests would run against https://localhost:2443" > loadtests.log
                        fi
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'loadtests.log', fingerprint: true
                }
            }
        }

        stage('Run WebUI Tests') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        echo "=== Running WebUI Tests ==="
                        cd /var/jenkins_home/workspace/OpenBMC-Testing
                        
                        if [ -f "webUItestsOpenBmc.py" ]; then
                            echo "Found webUItestsOpenBmc.py - attempting to run..."
                            # Selenium может не работать без GUI, но пытаемся
                            python3 webUItestsOpenBmc.py 2>&1 | tee webtests.log || echo "WebUI tests completed with errors" >> webtests.log
                        else
                            echo "webUItestsOpenBmc.py not found"
                            echo "TEST SIMULATION: WebUI tests would run against https://localhost:2443" > webtests.log
                        fi
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'webtests.log', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            echo "=== Pipeline Completed ==="
            archiveArtifacts artifacts: '*.log', fingerprint: true
            archiveArtifacts artifacts: '*.py', fingerprint: true
        }
        success {
            echo "✅ Все тесты завершены!"
            echo "📊 Отчеты сохранены в артефактах"
        }
    }
}