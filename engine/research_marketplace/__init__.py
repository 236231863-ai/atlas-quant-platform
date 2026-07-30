"""Research Marketplace - internal research exchange."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchTaskOffer:
    offer_id: str; task_description: str; required_skills: List[str]; reward: float = 1.0
    status: str = "open"
    def to_dict(self): return asdict(self)

@dataclass
class AgentBid:
    agent_id: str; offer_id: str; bid_amount: float; estimated_time: int = 1
    status: str = "pending"
    def to_dict(self): return asdict(self)

@dataclass
class ResearchContract:
    contract_id: str; offer: ResearchTaskOffer; bid: AgentBid; status: str = "active"
    def to_dict(self): return asdict(self)

class ResearchMarketplace:
    def __init__(self):
        self._offers: Dict[str, ResearchTaskOffer] = {}
        self._bids: List[AgentBid] = []
        self._contracts: Dict[str, ResearchContract] = {}
    def publish_task(self, offer: ResearchTaskOffer) -> ResearchTaskOffer:
        self._offers[offer.offer_id] = offer; return offer
    def bid(self, bid: AgentBid) -> AgentBid:
        self._bids.append(bid); return bid
    def assign(self, offer_id: str, agent_id: str) -> Optional[ResearchContract]:
        offer = self._offers.get(offer_id)
        if not offer or offer.status != "open": return None
        offer.status = "assigned"
        bid = next((b for b in self._bids if b.offer_id == offer_id and b.agent_id == agent_id), None)
        if not bid: bid = AgentBid(agent_id=agent_id, offer_id=offer_id, bid_amount=0)
        cid = f"contract_{offer_id}_{agent_id}"
        contract = ResearchContract(contract_id=cid, offer=offer, bid=bid)
        self._contracts[cid] = contract; return contract
    def evaluate(self, contract_id: str, score: float) -> bool:
        contract = self._contracts.get(contract_id)
        if not contract: return False
        contract.status = "completed"; return True
    def list_offers(self) -> List[ResearchTaskOffer]: return list(self._offers.values())
    def count_contracts(self) -> int: return len(self._contracts)
