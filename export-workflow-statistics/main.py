import os
import sys

sys.path.append(os.path.join(os.path.abspath('..'), "lib"))

import datetime
import config
import io
from collections import defaultdict
from rest_requests.request_error import RequestError
from args.digest_login import DigestLogin
from rest_requests.basic_requests import get_tenants
from rest_requests.workflow_requests import get_workflow_instances
from pathlib import Path


def main():
    """
    Export workflow statistics.
    """

    digest_login = DigestLogin(user=config.digest_user, password=config.digest_pw)
    tenants = get_tenants(config.url, digest_login)

    weeks = __get_weeks(datetime.date.fromisoformat(config.start_date), datetime.date.fromisoformat(config.end_date))
    count = defaultdict(int)
    tenant_total_counts = dict()

    tenant_dir = "tenant-statistics"
    Path(os.path.join(config.export_dir, tenant_dir)).mkdir(parents=True, exist_ok=True)

    for tenant in tenants:
        if tenant not in config.exclude_tenants:

            tenant_count = defaultdict(int)
            tenant_url = config.url_pattern.format(tenant) if config.url_pattern else config.url

            for workflow_definition in config.workflow_definitions:

                for i, week in enumerate(weeks):

                    from_date = "{}T00:00:00Z".format(week[0])
                    to_date = "{}T23:59:59Z".format(week[1])

                    params = {"state": "SUCCEEDED", "fromdate": from_date, "todate": to_date,
                              "workflowdefinition": workflow_definition, "startPage": "0",
                              "count": "1", "compact": "True"}
                    try:
                        workflow_instances = get_workflow_instances(tenant_url, digest_login, params)

                        count[i] += workflow_instances['totalCount']
                        tenant_count[i] += workflow_instances['totalCount']
                        print("{:30} {:>30} {:>3}".format(tenant, workflow_definition, i + config.week_offset + 1,
                                                          count[i]))
                    except RequestError as e:
                        print("Workflows for tenant {}, workflow definition {} and dates {} to {} could not be "
                              "requested: {}".format(tenant, workflow_definition, from_date, to_date, str(e)))

            tenant_total_count = 0
            with io.open(os.path.join(config.export_dir, tenant_dir, "{}-workflow-statistics.dat".format(tenant)),
                         'w') as file:
                for i, week in enumerate(weeks):
                    file.write("{}   {}\n".format(i + config.week_offset + 1, tenant_count[i]))
                    tenant_total_count += tenant_count[i]

            tenant_total_counts[tenant] = tenant_total_count

    sorted_tenant_total_counts = {k: v for k, v in sorted(tenant_total_counts.items(), key=lambda item: item[1],
                                                          reverse=True)}

    with io.open(os.path.join(config.export_dir, "filenames.txt"), 'w') as file:

        for tenant in sorted_tenant_total_counts.keys():
            if sorted_tenant_total_counts[tenant] != 0:
                print("{} {}".format(tenant, sorted_tenant_total_counts[tenant]))
                file.write("{}/{}-workflow-statistics.dat\n".format(tenant_dir, tenant))

    print("Done!\n")

    with io.open(os.path.join(config.export_dir, "workflow-statistics.dat"), 'w') as file:
        for i, week in enumerate(weeks):
            file.write("{}   {}\n".format(i + config.week_offset + 1, count[i]))


def __get_weeks(start_date, end_date):
    """
    Get a tuple with first and last date of the week for all weeks between the given start and end dates. Both of these
    should be the first day of a week, since we then count by offsets of 7.

    :param start_date:
    :type start_date: datetime.date
    :param end_date:
    :type end_date: datetime.date
    :return: list of tuples
    :rtype: list
    """
    weeks = []
    end_of_week_delta = datetime.timedelta(days=6)
    beginning_of_next_week_delta = datetime.timedelta(days=7)

    while start_date <= end_date:
        weeks.append((start_date, start_date + end_of_week_delta))
        start_date += beginning_of_next_week_delta
    return weeks


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborting process.")
        sys.exit(0)
