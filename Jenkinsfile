pipeline {
    agent any
    
    parameters {
        choice(
            name: 'TEST_TYPE',
            choices: ['ALL', 'AUTOTESTS', 'WEBUI', 'LOAD'],
            description: 'Select test type to run'
        )
    }
    
    stages {
        stage('Setup Environment') {
            steps {
                echo "🚀 Setting up test environment"
                sh '''
                    python3 --version || apt-get update && apt-get install -y python3 python3-pip
                    pip3 install selenium webdriver-manager requests pytest locust || true
                    apt-get install -y ipmitool || true
                '''
            }
        }
        
        stage('Start QEMU OpenBMC') {
            steps {
                echo "🔧 Starting QEMU OpenBMC simulation"
                sh '''
                    echo "Simulating QEMU OpenBMC startup..."
                    # В реальности: qemu-system-arm -m 256 -M romulus-bmc -nographic -drive file=openbmc.image,format=raw,if=mtd &
                    echo "QEMU started" > qemu_status.txt
                    sleep 10
                '''
            }
        }
        
        stage('Run Auto Tests (REST API)') {
            when {
                anyOf {
                    expression { params.TEST_TYPE == 'ALL' }
                    expression { params.TEST_TYPE == 'AUTOTESTS' }
                }
            }
            steps {
                echo "🔧 Running REST API Tests"
                sh '''
                    echo "Running lab6.py tests..."
                    mkdir -p reports/autotests
                    python3 lab6.py 2>&1 | tee reports/autotests/rest_api_results.txt
                '''
            }
            post {
                always {
                    junit 'reports/autotests/*.xml'
                    archiveArtifacts 'reports/autotests/*.txt'
                }
            }
        }
        
        stage('Run WebUI Tests (Selenium)') {
            when {
                anyOf {
                    expression { params.TEST_TYPE == 'ALL' }
                    expression { params.TEST_TYPE == 'WEBUI' }
                }
            }
            steps {
                echo "🌐 Running WebUI Tests"
                sh '''
                    echo "Running lab4.py tests..."
                    mkdir -p reports/webui
                    python3 lab4.py 2>&1 | tee reports/webui/selenium_results.txt
                '''
            }
            post {
                always {
                    junit 'reports/webui/*.xml'
                    archiveArtifacts 'reports/webui/*.txt'
                }
            }
        }
        
        stage('Run Load Tests (Locust)') {
            when {
                anyOf {
                    expression { params.TEST_TYPE == 'ALL' }
                    expression { params.TEST_TYPE == 'LOAD' }
                }
            }
            steps {
                echo "⚡ Running Load Tests"
                sh '''
                    echo "Running locust tests..."
                    mkdir -p reports/load
                    locust -f locustfile.py --headless -u 10 -r 1 --run-time 1m --html reports/load/locust_report.html 2>&1 | tee reports/load/locust_results.txt
                '''
            }
            post {
                always {
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: 'reports/load',
                        reportFiles: 'locust_report.html',
                        reportName: 'Load Test Report'
                    ])
                    archiveArtifacts 'reports/load/*'
                }
            }
        }
        
        stage('Stop QEMU') {
            steps {
                echo "🛑 Stopping QEMU"
                sh '''
                    echo "Stopping QEMU simulation..."
                    # pkill qemu-system-arm || true
                    echo "QEMU stopped" >> qemu_status.txt
                '''
            }
        }
    }
    
    post {
        always {
            echo "📊 Collecting test results"
            archiveArtifacts 'reports/**/*'
            archiveArtifacts '*.py'
        }
        success {
            echo "✅ All tests completed successfully!"
        }
        failure {
            echo "❌ Some tests failed!"
        }
    }
}