from communex.module.module import Module
from communex.client import CommuneClient
from substrateinterface import Keypair
from loguru import logger
import math
import warnings
import sys
from dotenv import load_dotenv
from polaris_subnet.validator.challenges import ChallengeGenerator
from polaris_subnet.validator.scoring import ScoringSystem 
from polaris_subnet.validator.verification import Verifier
import time 
import  asyncio
from datetime import datetime
from typing import List,Dict
import requests

class ValidatorNode(Module):
    def __init__(self, key: Keypair, netuid: int, client: CommuneClient, max_allowed_weights: int = 420):
        super().__init__()
        self.key = key
        self.netuid = netuid
        self.client = client
        self.max_allowed_weights = max_allowed_weights
        self.challenge_gen = ChallengeGenerator()
        self.verifier = Verifier()
        self.scoring = ScoringSystem()
        self.miner_data: Dict[str, float] = {}
        self.container_start_times: Dict[str, datetime] = {}  # {container_id: start_time}

    def track_miner_containers(self):
        """Fetch and update active containers for each miner."""
        # miners = self.get_miners()
        miners=["UhsJfZCngizQoslnKWoL", "UhsJfZCngizQoslnKWoLko"]
        active_miners=self.get_miner_list()
        if not active_miners:
            logger.warning("No active miners found.")
            return []
        logger.info("Processing miners and their containers...")
        results = self.process_miners(miners, active_miners)
        for result in results:
            self.miner_data[result['miner_uid']] = result['final_score']

        logger.info("Miner score processing complete.")
        logger.debug(f"Updated miner_data: {self.miner_data}")
            

    def get_miners(self) -> List[str]:
        """Fetch miners from the network."""
        try:
            miner_keys = self.client.query_map_key(self.netuid)
            # Extract and return the list of UIDs
            # return list(self.client.query_map_key(self.netuid).values())
            return list(miner_keys.keys())
        except Exception as e:
            logger.error(f"Error fetching miners: {e}")
            return []

    def get_containers_for_miner(self, miner_uid: str) -> List[str]:
        """Fetch container IDs associated with a miner."""
        try:
            response = requests.get(f"https://orchestrator-gekh.onrender.com/api/v1/containers/miner/{miner_uid}")
            if response.status_code == 200:
                return response.json()
            logger.warning(f"Failed to fetch containers for miner {miner_uid}. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching containers for miner {miner_uid}: {e}")
        return []

    def get_miner_list(self) -> List[Dict]:
        """Fetch verified miners from the network."""
        try:
            response = requests.get("https://orchestrator-gekh.onrender.com/api/v1/miners")
            if response.status_code == 200:
                miners_data = response.json()
                return [miner["id"] for miner in miners_data if miner["status"] == "verified"]
            logger.warning(f"Failed to fetch miners. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching miner list: {e}")
        return []

    def validate_container(self, container_id: str) -> Dict:
        """Send a challenge to a container and validate its response."""
        try:
            challenge = self.challenge_gen.generate_challenge(container_id)
            logger.debug(f"Generated challenge for container {container_id}: {challenge}")

            response = requests.put(
                f"http://localhost:8080/challenge/{container_id}",
                json=challenge,
                headers={"Content-Type": "application/json"}
            )
            result = response.json()

            if not self.verifier.verify_resource_usage(container_id, result):
                logger.warning(f"Verification failed for container {container_id}")
                return {}

            score = self.scoring.calculate_score(container_id, result)
            logger.info(f"Container {container_id} scored: {score}")
            return {"score": score, "result": result}

        except Exception as e:
            logger.error(f"Error validating container {container_id}: {e}")
            return {}
    
    def process_miners(self, miners: List[str], active_miners: List[Dict]) -> List[Dict]:
        """
        Process miners to validate their containers, calculate final scores,
        and return the results in the required format.

        Args:
            miners: List of miner UIDs to check.
            active_miners: List of active miners with their details.

        Returns:
            List of dictionaries with miner UID, final score, and number of rewarded containers.
        """
        results = []
        for miner in miners:
            if miner not in [m for m in active_miners]:
                logger.debug(f"Miner {miner} is not active. Skipping...")
                continue
            # Fetch containers for the miner
            containers = self.get_containers_for_miner(miner)
            total_termination_time = 0
            total_score = 0.0
            rewarded_containers = 0
            for container in containers:
                # Process only active containers with pending payment
                if container['status'] == 'terminated' and container['payment_status'] == 'pending':
                    scheduled_termination = container['subnet_details'].get('scheduled_termination', 0)
                    total_termination_time += scheduled_termination

                    # Validate the container
                    # validation_result = self.validate_container(container['container_id'])
                    # if validation_result:
                    #     rewarded_containers += 1
                    #     total_score += validation_result.get('score', 0.0)
                    total_score=0.5
                    rewarded_containers=2
            # If containers are processed, calculate the final score
            if rewarded_containers > 0:
                average_score = total_score / rewarded_containers
                final_score = average_score + total_termination_time
                results.append({
                    'miner_uid': 7,
                    'final_score': final_score
                })

        return results

    def update_container_payment_status(container_id: str):
        """
        Update the payment status of a container using the PATCH method.

        Args:
            container_id (str): The ID of the container to update.
            api_url (str): The API endpoint to update the container payment status.

        Returns:
            bool: True if the update is successful, False otherwise.
        """
        api_url: str = "https://orchestrator-gekh.onrender.com/api/v1/containers/{container_id}/payment"
        try:
            # Construct the full API URL
            full_url = api_url.format(container_id=container_id)

            # Data to be sent in the PATCH request
            data = {"status": "completed"}

            # Send the PATCH request
            response = requests.patch(full_url, json=data, headers={"Content-Type": "application/json"})

            # Check for successful update
            if response.status_code == 200:
                logger.info(f"Successfully updated payment status for container {container_id}.")
                return True
            else:
                logger.error(f"Failed to update payment status for container {container_id}. "
                            f"Status code: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error while updating payment status for container {container_id}: {e}")
            return False


    def cut_to_max_allowed_weights(self, score_dict: Dict[str, float]) -> Dict[str, float]:
        """Limit the number of weights to the max allowed."""
        if len(score_dict) > self.max_allowed_weights:
            sorted_scores = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_scores[:self.max_allowed_weights])
        return score_dict

    def normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to a range of 0 to 1."""
        max_score = max(scores.values(), default=1)
        return {uid: score / max_score for uid, score in scores.items()}
