from elasticsearch import AsyncElasticsearch
from app.core.config import settings
from app.core.logging import get_logger
from typing import Dict, Any, Optional, List

logger = get_logger(__name__)


class ElasticsearchClient:
    """Elasticsearch 클라이언트"""

    def __init__(self):
        self.client = AsyncElasticsearch(
            hosts=[
                f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"
            ]
        )
        logger.info(
            f"Elasticsearch client initialized with host: {settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"
        )

    async def ensure_index(
        self, index_name: str, mappings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """인덱스 존재 확인 및 생성"""
        try:
            if not await self.client.indices.exists(index=index_name):
                if mappings:
                    # 매핑이 있는 경우 매핑과 함께 인덱스 생성
                    await self.client.indices.create(
                        index=index_name, body={"mappings": mappings}
                    )
                else:
                    # 기본 설정으로 인덱스 생성
                    await self.client.indices.create(index=index_name)

                logger.info(f"Created Elasticsearch index: {index_name}")
                return True

            return True

        except Exception as e:
            logger.error(
                f"Failedt to ensure Elasticsearch index {index_name}: {str(e)}"
            )
            return False

    async def index_document(
        self, index_name: str, document: Dict[str, Any], doc_id: Optional[str] = None
    ) -> bool:
        """문서 인덱싱"""
        try:
            # 인덱스 존재 확인
            await self.ensure_index(index_name)

            await self.client.index(index=index_name, id=doc_id, document=document)

            logger.debug(f"Indexed document in {index_name} with ID {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to index document in Elasticsearch: {str(e)}")
            return False

    async def get_document(
        self, index_name: str, doc_id: str
    ) -> Optional[Dict[str, Any]]:
        """문서 조회"""
        try:
            response = await self.client.get(
                index=index_name,
                id=doc_id,
            )

            return response["_source"]

        except Exception as e:
            logger.error(f"Failed to get document from Elasticsearch: {str(e)}")
            return None

    async def update_document(
        self, index_name: str, doc_id: str, document: Dict[str, Any]
    ) -> bool:
        """문서 업데이트"""
        try:
            await self.client.update(
                index=index_name,
                id=doc_id,
                doc=document,
            )

            logger.debug(f"Updated document in {index_name} with ID {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update document in Elasticsearch: {str(e)}")
            return False

    async def search_documents(
        self,
        index_name: str,
        query: Dict[str, Any],
        from_: int = 0,
        size: int = 10,
        sort: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """문서 검색"""
        try:
            body = {"query": query, "from": from_, "size": size}

            if sort:
                body["sort"] = sort

            response = await self.client.search(index=index_name, body=body)

            # 결과 변환
            hits = response["hits"]
            results = {
                "total": hits["total"],
                "hits": [hit["_source"] for hit in hits["hits"]],
            }

            return results

        except Exception as e:
            logger.error(f"Failed to search documents in Elasticsearch: {str(e)}")
            return {"total": {"value": 0}, "hits": []}

    async def delete_document(self, index_name: str, doc_id: str) -> bool:
        """문서 삭제"""
        try:
            await self.client.delete(index=index_name, id=doc_id)

            logger.debug(f"Deleted document from {index_name} with ID {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document from Elasticsearch: {str(e)}")
            return False

    async def close(self):
        """클라이언트 연결 종료"""
        await self.client.close()


async def get_elasticsearch_client():
    """종속성 주입용 함수"""
    client = ElasticsearchClient()
    try:
        yield client
    finally:
        await client.close()
