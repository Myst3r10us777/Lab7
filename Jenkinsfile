pipeline {
    agent any

    stages {
        stage('Start QEMU OpenBMC') {
            steps {
                sh '''
                    echo "QEMU OpenBMC"
                    cd /var/jenkins_home/workspace/project
                    qemu-system-arm -m 512 -M romulus-bmc -nographic \\
                      -drive file=romulus/obmc-phosphor-image-romulus-20250927014348.static.mtd,format=raw,if=mtd \\
                      -net nic,model=ftgmac100 -net user,hostfwd=tcp::2222-:22,hostfwd=tcp::2443-:443,hostfwd=udp::2623-:623 &
                    echo $! > /var/jenkins_home/workspace/project/qemu.pid
                    sleep 90
                '''
            }
        }

        stage('autotestsOpenBmc') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        echo "autotests"
                        cd /var/jenkins_home/workspace/project
                        python3 -m pytest autotestsOpenBmc.py -v | tee /var/jenkins_home/workspace/project/autotests.log
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: '/var/jenkins_home/workspace/project/autotests.log', fingerprint: true
                }
            }
        }

        stage('loadtestsOpenBmc') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        echo "loadtests"
                        cd /var/jenkins_home/workspace/project
                        locust -f loadtestsOpenBmc.py --headless -u 1 -r 1 --run-time 30s --host=https://localhost:2443 | tee /var/jenkins_home/workspace/project/loadtests.log
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: '/var/jenkins_home/workspace/project/loadtests.log', fingerprint: true
                }
            }
        }

        stage('webUItestsOpenBmc') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        echo "WebUItests"
                        cd /var/jenkins_home/workspace/project
                        python3 -m pytest webUItestsOpenBmc.py -v | tee /var/jenkins_home/workspace/project/webtests.log
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: '/var/jenkins_home/workspace/project/webtests.log', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            sh '''
                echo "stop QEMU"
                if [ -f /var/jenkins_home/workspace/project/qemu.pid ]; then
                    kill $(cat /var/jenkins_home/workspace/project/qemu.pid) || true
                    rm -f /var/jenkins_home/workspace/project/qemu.pid
                fi
            '''
        }
        success {
            echo " Pipeline выполнен! Все тесты завершены."
        }
        unstable {
            echo "️ Pipeline выполнен с некоторыми ошибками тестов."
        }
        failure {
            echo "Pipeline завершился с ошибкой."
        }
    }
}