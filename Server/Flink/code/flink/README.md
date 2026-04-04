# 1. 환경 준비
./gradlew clean build

# 2. 예제 실행 (난이도순)
./gradlew runWordCount 2>&1 | grep -E "^[0-9]+>"                                            # ← 가장 먼저  # WordCountExample
./gradlew runWindowing 2>&1 | grep -E "^\(.*\)$"                                            # ← 두 번째   # WindowingExample
./gradlew runStateManagement 2>&1 | grep "User:"                                            # ← 세 번째   # StateManagementExample
./gradlew runCheckpoint 2>&1 | grep -E '\[입력:|!!!|==='                                     # ← 네 번째   # CheckpointExample
./gradlew runEventTime 2>&1 | grep -E "\[EVENT TIME\]|\[PROCESSING TIME\]|\[생성"            # ← 다섯 번째 # EventTimeExample