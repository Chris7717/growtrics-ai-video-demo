import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.pipeline.context import PipelineContext
from app.db.models.supported_concept import SupportedConcept

class ConceptResolver:
    async def run(self, session: AsyncSession, context: PipelineContext) -> None:
        """
        Stage 1: Resolve Concept
        - Normalize query
        - Match with canonical_query in supported_concepts
        """
        normalized = self._normalize_query(context.query)
        
        # Simple match: find concept whose canonical_query roughly matches
        # In a real app, this might use NLP or embeddings
        result = await session.execute(select(SupportedConcept).where(SupportedConcept.is_active == True))
        concepts = result.scalars().all()
        
        best_match = None
        for concept in concepts:
            norm_canonical = self._normalize_query(concept.canonical_query)
            if normalized in norm_canonical or norm_canonical in normalized:
                best_match = concept
                break
                
        if not best_match:
            # Fallback to a default if none matches, or raise exception
            # For simplicity, if we find any match, we use it. Otherwise, let's just pick the first one for the demo.
            if concepts:
                best_match = concepts[0]
            else:
                raise Exception("UNSUPPORTED_CONCEPT: No active concepts found.")
                
        context.concept = best_match
        context.job.concept_id = best_match.id

    def _normalize_query(self, query: str) -> str:
        # Remove punctuation and lowercase
        translator = str.maketrans('', '', string.punctuation)
        return query.translate(translator).lower().strip()
