import mock
import pytest

from datadog_checks.base.types import ServiceCheck

pytestmark = [pytest.mark.unit]


@pytest.mark.parametrize(
    'instance, cloudera_version, read_clusters, read_events, dd_run_check_count, expected_service_checks',
    [
        (
            {'api_url': 'http://localhost:8080/api/v48/'},
            {'exception': 'Service not available'},
            {'number': 0},
            {'number': 0},
            1,
            [
                {
                    'status': ServiceCheck.CRITICAL,
                    'message': 'Cloudera API Client is none: Service not available',
                    'tags': ['api_url:http://localhost:8080/api/v48/'],
                }
            ],
        ),
        (
            {'api_url': 'http://localhost:8080/api/v48/', 'tags': ['new_tag']},
            {'exception': 'Service not available'},
            {'number': 0},
            {'number': 0},
            1,
            [
                {
                    'status': ServiceCheck.CRITICAL,
                    'message': 'Cloudera API Client is none: Service not available',
                    'tags': ['api_url:http://localhost:8080/api/v48/', 'new_tag'],
                }
            ],
        ),
        (
            {'api_url': 'http://localhost:8080/api/v48/'},
            {},
            {'number': 0},
            {'number': 0},
            1,
            [
                {
                    'status': ServiceCheck.CRITICAL,
                    'message': 'Cloudera API Client is none: Cloudera Manager Version is unsupported or unknown: None',
                    'tags': ['api_url:http://localhost:8080/api/v48/'],
                }
            ],
        ),
        (
            {'api_url': 'http://localhost:8080/api/v48/', 'tags': ['new_tag']},
            {},
            {'number': 0},
            {'number': 0},
            1,
            [
                {
                    'status': ServiceCheck.CRITICAL,
                    'message': 'Cloudera API Client is none: Cloudera Manager Version is unsupported or unknown: None',
                    'tags': ['api_url:http://localhost:8080/api/v48/', 'new_tag'],
                }
            ],
        ),
        (
            {'api_url': 'http://localhost:8080/api/v48/'},
            {'version': '5.0.0'},
            {'number': 0},
            {'number': 0},
            1,
            [
                {
                    'status': ServiceCheck.CRITICAL,
                    'message': 'Cloudera API Client is none: Cloudera Manager Version is unsupported or unknown: 5.0.0',
                    'tags': ['api_url:http://localhost:8080/api/v48/'],
                }
            ],
        ),
        (
            {'api_url': 'http://localhost:8080/api/v48/', 'tags': ['new_tag']},
            {'version': '5.0.0'},
            {'number': 0},
            {'number': 0},
            1,
            [
                {
                    'status': ServiceCheck.CRITICAL,
                    'message': 'Cloudera API Client is none: Cloudera Manager Version is unsupported or unknown: 5.0.0',
                    'tags': ['api_url:http://localhost:8080/api/v48/', 'new_tag'],
                }
            ],
        ),
        (
            {'api_url': 'http://localhost:8080/api/v48/'},
            {'version': '7.0.0'},
            {'number': 0},
            {'number': 0},
            1,
            [{'status': ServiceCheck.OK, 'message': None, 'tags': ['api_url:http://localhost:8080/api/v48/']}],
        ),
        (
            {'api_url': 'http://localhost:8080/api/v48/', 'tags': ['new_tag']},
            {'version': '7.0.0'},
            {'number': 0},
            {'number': 0},
            1,
            [
                {
                    'status': ServiceCheck.OK,
                    'message': None,
                    'tags': ['api_url:http://localhost:8080/api/v48/', 'new_tag'],
                }
            ],
        ),
    ],
    ids=[
        'exception',
        'exception with custom tags',
        'none',
        'none with custom tags',
        'unsupported',
        'unsupported with custom tags',
        'supported',
        'supported with custom tags',
    ],
    indirect=['instance', 'cloudera_version', 'read_clusters', 'read_events'],
)
def test_version(
    aggregator,
    dd_run_check,
    cloudera_check,
    instance,
    cloudera_version,
    read_clusters,
    read_events,
    dd_run_check_count,
    expected_service_checks,
):
    with mock.patch(
        'datadog_checks.cloudera.client.cm_client.CmClient.get_version',
        side_effect=[cloudera_version],
    ), mock.patch(
        'datadog_checks.cloudera.client.cm_client.CmClient.read_clusters',
        side_effect=[read_clusters],
    ), mock.patch(
        'datadog_checks.cloudera.client.cm_client.CmClient.read_events',
        side_effect=[read_events],
    ):
        check = cloudera_check(instance)
        for _ in range(dd_run_check_count):
            dd_run_check(check)
        for expected_service_check in expected_service_checks:
            aggregator.assert_service_check(
                'cloudera.can_connect',
                count=expected_service_check.get('count'),
                status=expected_service_check.get('status'),
                message=expected_service_check.get('message'),
                tags=expected_service_check.get('tags'),
            )
