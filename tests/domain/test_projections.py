import pytest
from hypothesis import given

from challenge.domain.model.translation import Translation
from challenge.domain.projections import TranslationProjections
from challenge.persistence import create_db, create_tables
from challenge.persistence.eventstore import model as e_model  # noqa: F401
from challenge.persistence.eventstore.postgresql import PostgresEventStore
from challenge.persistence.projections import model as p_model  # noqa: F401
from challenge.persistence.projections.postgresql import PostgresTranslation
from tests.fixtures.strategies import valid_translation, valid_translation_list


class TestRepositories:
    @pytest.fixture
    def projections(self):
        db = create_db()
        create_tables(db)
        return TranslationProjections(PostgresTranslation())

    @given(translation=valid_translation())
    def test_save_aggregate_persists_aggregate(self, repository, translation):
        repository.save(translation)
        aggregate = repository.get(translation.id)

        assert isinstance(aggregate, Translation)
        assert translation.as_dict() == aggregate.as_dict()

    @given(translations=valid_translation_list())
    def test_get_returns_aggregate(self, repository, translations):
        for translation in translations:
            repository.save(translation)

        for translation in translations:
            aggregate = repository.get(translation.id)
            assert isinstance(aggregate, Translation)
            assert translation.as_dict() == aggregate.as_dict()
