import asyncio
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.db.models.supported_concept import SupportedConcept

CONCEPTS = [
    {
        "code": "ph_scale",
        "canonical_query": "Explain the pH scale",
        "title": "Understanding the pH Scale",
        "required_facts": ["pH measures acidity/alkalinity", "Scale is 0-14", "7 is neutral"],
        "allowed_visual_types": ["diagram", "chart"],
        "template_path": "templates/ph_scale.json",
        "is_active": True
    },
    {
        "code": "covalent_bonds",
        "canonical_query": "What are covalent bonds?",
        "title": "Covalent Bonds",
        "required_facts": ["Sharing of electrons", "Occurs between nonmetals", "Forms molecules"],
        "allowed_visual_types": ["animation", "diagram"],
        "template_path": "templates/covalent_bonds.json",
        "is_active": True
    },
    {
        "code": "ionic_vs_covalent",
        "canonical_query": "Ionic vs Covalent bonds",
        "title": "Ionic vs Covalent Bonding",
        "required_facts": ["Ionic transfers electrons", "Covalent shares electrons", "Differences in properties"],
        "allowed_visual_types": ["comparison_table", "animation"],
        "template_path": "templates/ionic_vs_covalent.json",
        "is_active": True
    }
]

async def seed_concepts():
    async with async_session() as session:
        for concept_data in CONCEPTS:
            stmt = insert(SupportedConcept).values(**concept_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['code'],
                set_={
                    'canonical_query': stmt.excluded.canonical_query,
                    'title': stmt.excluded.title,
                    'required_facts': stmt.excluded.required_facts,
                    'allowed_visual_types': stmt.excluded.allowed_visual_types,
                    'template_path': stmt.excluded.template_path,
                    'is_active': stmt.excluded.is_active
                }
            )
            await session.execute(stmt)
        await session.commit()
        print("Seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_concepts())
