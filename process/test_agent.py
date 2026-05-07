import asyncio
import pathlib
import sys
from uuid import uuid4

from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from smartshopper_agent.runtime import run_agent

load_dotenv(ROOT / ".env")


TEST_QUERIES = [
    "Rekomendasikan dress cotton untuk acara santai di bawah 50 dollar.",
    "Bagaimana cara refund kalau barang yang saya terima rusak?",
    "Saya mau beli atasan yang nyaman, lalu pengirimannya berapa lama?",
]


async def main() -> None:
    session_id = str(uuid4())
    for query in TEST_QUERIES:
        print("\nUSER:", query)
        answer = await run_agent(query, user_id="test_user", session_id=session_id)
        print("ASSISTANT:", answer)


if __name__ == "__main__":
    asyncio.run(main())
