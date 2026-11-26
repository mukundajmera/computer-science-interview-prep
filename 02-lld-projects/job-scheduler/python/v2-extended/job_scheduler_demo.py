from job_scheduler import JobScheduler


def main() -> None:
    service = JobScheduler()
    print(service.describe())


if __name__ == "__main__":
    main()
