import os

import pytest

from operators.flux_gitops_operator import FluxGitopsOperator


os.environ['GITOPS_APP_URL'] = 'https://example.com/testing'


def test_get_commit_id_from_gitrepository_new_revision_new_key(operator):
    commit_id = operator.get_commit_id({
        'involvedObject': {
            'kind': 'GitRepository',
        },
        'metadata': {
            'source.toolkit.fluxcd.io/revision':
                'main@sha1:40d6b21b888db0ca794876cf7bdd399e3da2137e',
        }
    })

    assert commit_id == '40d6b21b888db0ca794876cf7bdd399e3da2137e'


def test_get_commit_id_from_gitrepository_old_revision_new_key(operator):
    commit_id = operator.get_commit_id({
        'involvedObject': {
            'kind': 'GitRepository',
        },
        'metadata': {
            'source.toolkit.fluxcd.io/revision': 'main/40d6b21b888db0ca794876cf7bdd399e3da2137e',
        }
    })

    assert commit_id == '40d6b21b888db0ca794876cf7bdd399e3da2137e'


def test_get_commit_id_from_gitrepository_old_revision_and_old_key(operator):
    commit_id = operator.get_commit_id({
        'involvedObject': {
            'kind': 'GitRepository',
        },
        'metadata': {
            'revision': 'main/40d6b21b888db0ca794876cf7bdd399e3da2137e',
        }
    })

    assert commit_id == '40d6b21b888db0ca794876cf7bdd399e3da2137e'


def test_get_commit_id_from_gitrepository_early_revision_and_old_key(operator):
    commit_id = operator.get_commit_id({
        'involvedObject': {
            'kind': 'GitRepository',
        },
        'metadata': {
            'message': 'Fetched revision: main/40d6b21b888db0ca794876cf7bdd399e3da2137e',
        }
    })

    assert commit_id == '40d6b21b888db0ca794876cf7bdd399e3da2137e'


def test_get_commit_id_from_kustomization_new_revision_and_new_key(operator):
    # kustomize-controller v0.41+
    commit_id = operator.get_commit_id({
        'involvedObject': {
            'kind': 'Kustomization',
        },
        'metadata': {
            'kustomize.toolkit.fluxcd.io/revision':
                'main@sha1:40d6b21b888db0ca794876cf7bdd399e3da2137e',
        }
    })

    assert commit_id == '40d6b21b888db0ca794876cf7bdd399e3da2137e'


def test_get_commit_id_from_kustomization_old_revision_and_new_key(operator):
    # kustomize-controller v0.18+
    commit_id = operator.get_commit_id({
        'involvedObject': {
            'kind': 'Kustomization',
        },
        'metadata': {
            'kustomize.toolkit.fluxcd.io/revision':
                'main/40d6b21b888db0ca794876cf7bdd399e3da2137e',
        }
    })

    assert commit_id == '40d6b21b888db0ca794876cf7bdd399e3da2137e'


def test_get_commit_id_from_kustomization_old_revision_and_old_key(operator):
    commit_id = operator.get_commit_id({
        'involvedObject': {
            'kind': 'Kustomization',
        },
        'metadata': {
            'revision': 'main/40d6b21b888db0ca794876cf7bdd399e3da2137e',
        }
    })

    assert commit_id == '40d6b21b888db0ca794876cf7bdd399e3da2137e'


def test_get_commit_id_from_other_resource(operator):
    commit_id = operator.get_commit_id({
        'involvedObject': {
            'kind': 'HelmRepository',
        },
        'metadata': {
            'kustomize.toolkit.fluxcd.io/revision':
                'main@sha1:40d6b21b888db0ca794876cf7bdd399e3da2137e',
        }
    })

    assert commit_id == ''


@pytest.fixture
def operator():
    return FluxGitopsOperator()
