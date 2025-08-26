from internal.models_database.categories import CategoriesModel
from internal.repository.base_repository import BaseRepository
from internal.repository.data_mapper.data_mappers import CategoryDataMapper


class CategoryRepository(BaseRepository):
    model = CategoriesModel
    mapper = CategoryDataMapper
