"""
Nancy Knowledge Packet Processor
Handles processing, validation, and routing of Nancy Knowledge Packets.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

from schemas.knowledge_packet import NancyKnowledgePacket, KnowledgePacketValidator
from .config_manager import NancyConfiguration
from .search import AnalyticalBrain
from .knowledge_graph import GraphBrain
from .nlp import VectorBrain

logger = logging.getLogger(__name__)


class ProcessingStatus(str, Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class PacketProcessingResult:
    """Result of processing a Knowledge Packet."""
    
    def __init__(self, packet_id: str, status: ProcessingStatus, 
                 message: str = "", metrics: Optional[Dict[str, Any]] = None,
                 errors: Optional[List[str]] = None):
        self.packet_id = packet_id
        self.status = status
        self.message = message
        self.metrics = metrics or {}
        self.errors = errors or []
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "packet_id": self.packet_id,
            "status": self.status.value,
            "message": self.message,
            "metrics": self.metrics,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat() + "Z"
        }


class BrainRouter:
    """Routes Knowledge Packets to appropriate brains based on content and hints."""
    
    def __init__(self, config: NancyConfiguration):
        self.config = config
        
    def determine_routing(self, packet: NancyKnowledgePacket) -> Dict[str, bool]:
        """
        Determine which brains should process this packet.
        
        Args:
            packet: Knowledge Packet to route
            
        Returns:
            Dictionary indicating which brains to use
        """
        routing = {
            "vector": False,
            "analytical": False,
            "graph": False,
            "metadata": True  # Always store metadata
        }
        
        # Check processing hints first
        hints = packet.processing_hints
        if hints:
            priority_brain = hints.get("priority_brain", "auto")
            
            if priority_brain == "vector":
                routing["vector"] = True
            elif priority_brain == "analytical":
                routing["analytical"] = True
            elif priority_brain == "graph":
                routing["graph"] = True
            elif priority_brain == "auto":
                # Auto-detect based on content
                routing.update(self._auto_detect_routing(packet))
        else:
            # Auto-detect based on content
            routing.update(self._auto_detect_routing(packet))
        
        return routing
    
    def _auto_detect_routing(self, packet: NancyKnowledgePacket) -> Dict[str, bool]:
        """Auto-detect routing based on packet content."""
        routing = {
            "vector": packet.has_vector_data(),
            "analytical": packet.has_analytical_data(),
            "graph": packet.has_graph_data()
        }
        
        # If no specific data types, default to vector for text content
        if not any(routing.values()):
            routing["vector"] = True
        
        return routing


class KnowledgePacketProcessor:
    """
    Processes Nancy Knowledge Packets through the Four-Brain architecture.
    """
    
    def __init__(self, config: NancyConfiguration):
        self.config = config
        self.validator = KnowledgePacketValidator()
        self.router = BrainRouter(config)
        
        # Initialize brains
        self.vector_brain = VectorBrain()
        self.analytical_brain = AnalyticalBrain()
        self.graph_brain = GraphBrain()
        
        # Processing metrics
        self.total_processed = 0
        self.total_failed = 0
        self.processing_times = []
        
        # Processing hooks
        self.pre_processing_hooks: List[Callable] = []
        self.post_processing_hooks: List[Callable] = []
    
    def add_pre_processing_hook(self, hook: Callable[[NancyKnowledgePacket], None]):
        """Add a hook to be called before processing each packet."""
        self.pre_processing_hooks.append(hook)
    
    def add_post_processing_hook(self, hook: Callable[[NancyKnowledgePacket, PacketProcessingResult], None]):
        """Add a hook to be called after processing each packet."""
        self.post_processing_hooks.append(hook)
    
    async def process_packet(self, packet: NancyKnowledgePacket) -> PacketProcessingResult:
        """
        Process a single Knowledge Packet.
        
        Args:
            packet: Validated Knowledge Packet to process
            
        Returns:
            PacketProcessingResult containing processing outcome
        """
        start_time = datetime.utcnow()
        
        try:
            logger.debug(f"Processing Knowledge Packet {packet.packet_id}")
            
            # Run pre-processing hooks
            for hook in self.pre_processing_hooks:
                try:
                    hook(packet)
                except Exception as e:
                    logger.warning(f"Pre-processing hook failed: {e}")
            
            # Validate packet
            self.validator.validate_packet(packet)
            
            # Determine routing
            routing = self.router.determine_routing(packet)
            
            # Process through selected brains
            brain_results = {}
            errors = []
            
            if routing.get("vector"):
                try:
                    brain_results["vector"] = await self._process_vector_brain(packet)
                except Exception as e:
                    errors.append(f"Vector brain processing failed: {e}")
                    logger.error(f"Vector brain processing failed for packet {packet.packet_id}: {e}")
            
            if routing.get("analytical"):
                try:
                    brain_results["analytical"] = await self._process_analytical_brain(packet)
                except Exception as e:
                    errors.append(f"Analytical brain processing failed: {e}")
                    logger.error(f"Analytical brain processing failed for packet {packet.packet_id}: {e}")
            
            if routing.get("graph"):
                try:
                    brain_results["graph"] = await self._process_graph_brain(packet)
                except Exception as e:
                    errors.append(f"Graph brain processing failed: {e}")
                    logger.error(f"Graph brain processing failed for packet {packet.packet_id}: {e}")
            
            if routing.get("metadata"):
                try:
                    brain_results["metadata"] = await self._process_metadata(packet)
                except Exception as e:
                    errors.append(f"Metadata processing failed: {e}")
                    logger.error(f"Metadata processing failed for packet {packet.packet_id}: {e}")
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.processing_times.append(processing_time)
            
            # Create result
            if errors:
                status = ProcessingStatus.FAILED if len(errors) == len(brain_results) else ProcessingStatus.COMPLETED
                message = f"Processed with {len(errors)} errors"
            else:
                status = ProcessingStatus.COMPLETED
                message = f"Successfully processed through {len(brain_results)} brains"
            
            result = PacketProcessingResult(
                packet_id=packet.packet_id,
                status=status,
                message=message,
                metrics={
                    "processing_time_seconds": processing_time,
                    "brains_processed": list(brain_results.keys()),
                    "routing_decisions": routing
                },
                errors=errors
            )
            
            # Update metrics
            if status == ProcessingStatus.COMPLETED:
                self.total_processed += 1
            else:
                self.total_failed += 1
            
            # Run post-processing hooks
            for hook in self.post_processing_hooks:
                try:
                    hook(packet, result)
                except Exception as e:
                    logger.warning(f"Post-processing hook failed: {e}")
            
            logger.info(f"Processed Knowledge Packet {packet.packet_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.total_failed += 1
            
            logger.error(f"Failed to process Knowledge Packet {packet.packet_id}: {e}")
            
            return PacketProcessingResult(
                packet_id=packet.packet_id,
                status=ProcessingStatus.FAILED,
                message=f"Processing failed: {e}",
                metrics={"processing_time_seconds": processing_time},
                errors=[str(e)]
            )
    
    async def _process_vector_brain(self, packet: NancyKnowledgePacket) -> Dict[str, Any]:
        """Process packet through Vector Brain."""
        vector_data = packet.content.get("vector_data", {})
        chunks = vector_data.get("chunks", [])
        
        processed_chunks = 0
        
        for chunk in chunks:
            chunk_text = chunk.get("text", "")
            chunk_metadata = chunk.get("chunk_metadata", {})
            
            # Enhance metadata with packet information
            enhanced_metadata = {
                **chunk_metadata,
                "packet_id": packet.packet_id,
                "source_file": packet.source.get("original_location"),
                "author": packet.metadata.get("author"),
                "title": packet.metadata.get("title"),
                "content_type": packet.source.get("content_type"),
                "mcp_server": packet.source.get("mcp_server")
            }
            
            # Generate document ID for chunk
            doc_id = f"{packet.packet_id}_{chunk.get('chunk_id', f'chunk_{processed_chunks}')}"
            
            # Store in vector brain
            self.vector_brain.add_text(
                text=chunk_text,
                metadata=enhanced_metadata,
                doc_id=doc_id
            )
            
            processed_chunks += 1
        
        return {
            "chunks_processed": processed_chunks,
            "embedding_model": vector_data.get("embedding_model"),
            "chunk_strategy": vector_data.get("chunk_strategy")
        }
    
    async def _process_analytical_brain(self, packet: NancyKnowledgePacket) -> Dict[str, Any]:
        """Process packet through Analytical Brain."""
        analytical_data = packet.content.get("analytical_data", {})
        
        # Process structured fields
        structured_fields = analytical_data.get("structured_fields", {})
        tables_processed = 0
        
        # Process table data
        table_data = analytical_data.get("table_data", [])
        for table in table_data:
            # TODO: Implement table data storage in analytical brain
            # For now, just count tables
            tables_processed += 1
        
        # Process time series data
        time_series = analytical_data.get("time_series", [])
        
        return {
            "structured_fields_count": len(structured_fields),
            "tables_processed": tables_processed,
            "time_series_points": len(time_series),
            "statistics": analytical_data.get("statistics", {})
        }
    
    async def _process_graph_brain(self, packet: NancyKnowledgePacket) -> Dict[str, Any]:
        """Process packet through Graph Brain."""
        graph_data = packet.content.get("graph_data", {})
        
        entities_created = 0
        relationships_created = 0
        
        # Process entities
        entities = graph_data.get("entities", [])
        for entity in entities:
            entity_type = entity.get("type")
            entity_name = entity.get("name")
            properties = entity.get("properties", {})
            
            # Enhance properties with packet context
            enhanced_properties = {
                **properties,
                "packet_id": packet.packet_id,
                "source_file": packet.source.get("original_location"),
                "extraction_confidence": entity.get("confidence", 1.0)
            }
            
            # Create entity node
            self.graph_brain.add_concept_node(entity_name, entity_type)
            entities_created += 1
        
        # Process relationships
        relationships = graph_data.get("relationships", [])
        for rel in relationships:
            source = rel.get("source", {})
            target = rel.get("target", {})
            rel_type = rel.get("relationship")
            rel_properties = rel.get("properties", {})
            
            # Create context from packet
            context = f"From {packet.metadata.get('title', 'Unknown')} (packet: {packet.packet_id})"
            
            # Create relationship
            self.graph_brain.add_relationship(
                source_node_label=source.get("type"),
                source_node_name=source.get("name"),
                relationship_type=rel_type,
                target_node_label=target.get("type"),
                target_node_name=target.get("name"),
                context=context
            )
            relationships_created += 1
        
        return {
            "entities_created": entities_created,
            "relationships_created": relationships_created,
            "extraction_method": graph_data.get("context", {}).get("extraction_method")
        }
    
    async def _process_metadata(self, packet: NancyKnowledgePacket) -> Dict[str, Any]:
        """Process packet metadata through Analytical Brain."""
        try:
            # Insert document metadata
            self.analytical_brain.insert_document_metadata(
                doc_id=packet.packet_id,
                filename=packet.metadata.get("title", "Unknown"),
                size=packet.metadata.get("file_size", 0),
                file_type=packet.source.get("content_type", "unknown")
            )
            
            return {
                "metadata_stored": True,
                "document_id": packet.packet_id,
                "file_type": packet.source.get("content_type")
            }
            
        except Exception as e:
            logger.error(f"Failed to store metadata for packet {packet.packet_id}: {e}")
            raise
    
    async def process_batch(self, packets: List[NancyKnowledgePacket]) -> List[PacketProcessingResult]:
        """
        Process a batch of Knowledge Packets concurrently.
        
        Args:
            packets: List of Knowledge Packets to process
            
        Returns:
            List of PacketProcessingResult objects
        """
        logger.info(f"Processing batch of {len(packets)} Knowledge Packets")
        
        # Process packets concurrently
        tasks = [self.process_packet(packet) for packet in packets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed for packet {packets[i].packet_id}: {result}")
                processed_results.append(
                    PacketProcessingResult(
                        packet_id=packets[i].packet_id,
                        status=ProcessingStatus.FAILED,
                        message=f"Batch processing exception: {result}",
                        errors=[str(result)]
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing performance metrics."""
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        return {
            "total_processed": self.total_processed,
            "total_failed": self.total_failed,
            "success_rate": self.total_processed / (self.total_processed + self.total_failed) if (self.total_processed + self.total_failed) > 0 else 0,
            "average_processing_time_seconds": avg_processing_time,
            "min_processing_time_seconds": min(self.processing_times) if self.processing_times else 0,
            "max_processing_time_seconds": max(self.processing_times) if self.processing_times else 0,
            "total_processing_batches": len(self.processing_times)
        }
    
    def reset_metrics(self):
        """Reset processing metrics."""
        self.total_processed = 0
        self.total_failed = 0
        self.processing_times.clear()


class PacketProcessingQueue:
    """Manages a queue of Knowledge Packets for processing."""
    
    def __init__(self, processor: KnowledgePacketProcessor, max_concurrent: int = 5):
        self.processor = processor
        self.max_concurrent = max_concurrent
        self.queue = asyncio.Queue()
        self.processing_tasks: List[asyncio.Task] = []
        self.is_running = False
        
    async def start(self):
        """Start the processing queue."""
        self.is_running = True
        
        # Start concurrent processing tasks
        for i in range(self.max_concurrent):
            task = asyncio.create_task(self._process_queue())
            self.processing_tasks.append(task)
        
        logger.info(f"Started packet processing queue with {self.max_concurrent} concurrent workers")
    
    async def stop(self):
        """Stop the processing queue."""
        self.is_running = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        self.processing_tasks.clear()
        
        logger.info("Stopped packet processing queue")
    
    async def enqueue(self, packet: NancyKnowledgePacket):
        """Add a packet to the processing queue."""
        await self.queue.put(packet)
    
    async def _process_queue(self):
        """Process packets from the queue."""
        while self.is_running:
            try:
                # Get packet from queue with timeout
                packet = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                # Process packet
                result = await self.processor.process_packet(packet)
                
                # Mark task as done
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                # Normal timeout, continue processing
                continue
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            "queue_size": self.queue.qsize(),
            "active_workers": len(self.processing_tasks),
            "is_running": self.is_running
        }