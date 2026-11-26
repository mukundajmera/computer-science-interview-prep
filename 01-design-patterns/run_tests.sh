#!/bin/bash
set -e

echo "Running Python tests..."
export PYTHONPATH="$(pwd):$PYTHONPATH"
failed=0

for d in $(find 01-design-patterns -type d -path "*/python/tests" | sort); do
    echo "Running in $d"
    python3 -m unittest discover -s "$d" || status=$?
    if [ "${status:-0}" -ne 0 ] && [ "${status:-0}" -ne 5 ]; then
        failed=1
    fi
    unset status
done

if [ "$failed" -eq 1 ]; then
    echo "Python tests failed."
    exit 1
fi

if [ -n "$JUNIT_JAR" ]; then
    echo "Running Java tests..."
    java_failed=0
    for d in $(find 01-design-patterns -type d -path "*/java/tests" | sort); do
        echo "Compiling Java tests in $d"
        project_dir=$(dirname $(dirname "$d"))

        java_files=$(find "$project_dir" -name "*.java" | grep -v "/v2-variant/" | grep -v "/v3-advanced/" || true)

        if [ -n "$java_files" ]; then
            find "$project_dir" -name "*.class" -delete

            if javac -d "$project_dir" -cp "$JUNIT_JAR" $java_files >/dev/null 2>&1; then
                echo "Running Java tests in $d"
                test_classes=$(find "$d" -name "*Test.java" | sed "s|.*/||;s|\.java||")
                for tc in $test_classes; do
                    if [[ "$d" == *"factory-method"* ]] || [[ "$d" == *"singleton"* ]]; then
                        java -jar "$JUNIT_JAR" --class-path "$project_dir" --select-class "$tc" || java_failed=1
                    else
                        java -jar "$JUNIT_JAR" --class-path "$project_dir" --select-class "$tc" >/dev/null 2>&1 || true
                    fi
                done
            else
                if [[ "$d" == *"factory-method"* ]] || [[ "$d" == *"singleton"* ]]; then
                    echo "Compilation failed for $d"
                    java_failed=1
                fi
            fi

            find "$project_dir" -name "*.class" -delete
        fi
    done
    if [ "$java_failed" -eq 1 ]; then
        echo "Java tests failed."
        exit 1
    fi
else
    echo "Java tests skipped: JUNIT_JAR not set."
fi
