# -*- coding: utf-8 -*-
# Frappe Assistant Core - AI Assistant integration for Frappe Framework
# Copyright (C) 2025 Paul Clinton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Business Intelligence Dashboard Recommendations - Professional BI best practices tool

Provides industry-standard recommendations for professional dashboard creation:
- Business domain specific KPI recommendations
- Audience-appropriate design principles  
- Implementation best practices
- Common mistakes to avoid
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class GetBIRecommendations(BaseTool):
    """Business Intelligence Dashboard Best Practices and Recommendations"""
    
    def __init__(self):
        super().__init__()
        self.name = "get_bi_recommendations"
        self.description = "Get industry-standard recommendations for professional dashboard creation"
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "business_domain": {
                    "type": "string",
                    "enum": ["sales", "finance", "operations", "hr", "executive"],
                    "description": "Business domain for specific recommendations"
                },
                "audience_level": {
                    "type": "string",
                    "enum": ["executive", "management", "operational"],
                    "description": "Target audience level"
                },
                "current_pain_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Current dashboard challenges or pain points"
                }
            },
            "required": ["business_domain", "audience_level"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide BI dashboard recommendations"""
        try:
            domain = arguments.get("business_domain")
            audience = arguments.get("audience_level")
            pain_points = arguments.get("current_pain_points", [])
            
            recommendations = self._generate_bi_recommendations(domain, audience, pain_points)
            
            return {
                "success": True,
                "business_domain": domain,
                "audience_level": audience,
                **recommendations
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_bi_recommendations(self, domain: str, audience: str, pain_points: List[str]) -> Dict[str, Any]:
        """Generate comprehensive BI recommendations"""
        
        return {
            "recommended_kpis": self._get_domain_kpis(domain),
            "design_principles": self._get_design_principles(audience),
            "implementation_best_practices": [
                "Start with 3-5 core KPIs, expand gradually",
                "Ensure data quality and consistency",
                "Use consistent time periods across metrics",
                "Implement proper user access controls",
                "Plan for mobile accessibility"
            ],
            "common_mistakes_to_avoid": [
                "Too many metrics on one screen",
                "Poor color choices affecting readability", 
                "Missing benchmarks or targets",
                "Inconsistent data refresh schedules",
                "Ignoring user feedback during development"
            ],
            "recommended_tools": [
                "Use create_bi_dashboard for professional implementation",
                "Leverage Frappe Workspace for modern UX",
                "Implement KPI cards with trend indicators",
                "Use consistent color schemes (Red/Amber/Green)"
            ],
            "next_steps": [
                f"Create {domain} dashboard using create_bi_dashboard tool",
                f"Configure for {audience}-level detail",
                "Test with actual users before full deployment",
                "Set up regular review and optimization schedule"
            ]
        }
    
    def _get_domain_kpis(self, domain: str) -> List[str]:
        """Get recommended KPIs for business domain"""
        kpis = {
            "sales": ["Revenue Growth", "Win Rate", "Sales Velocity", "Pipeline Value"],
            "finance": ["Gross Margin", "Cash Flow", "Current Ratio", "DSO"],
            "operations": ["OEE", "Quality Rate", "Cycle Time", "On-Time Delivery"],
            "hr": ["Employee Retention", "Engagement Score", "Time to Hire"],
            "executive": ["Revenue Growth", "Profit Margin", "Customer Satisfaction"]
        }
        return kpis.get(domain, [])
    
    def _get_design_principles(self, audience: str) -> List[str]:
        """Get design principles for audience level"""
        principles = {
            "executive": [
                "Minimal design with maximum insight",
                "Focus on trends and exceptions only",
                "Use traffic light indicators (Red/Amber/Green)",
                "Limit to 5-7 key metrics maximum"
            ],
            "management": [
                "Balance overview with actionable detail",
                "Include period-over-period comparisons",
                "Show performance against targets",
                "Use consistent visual hierarchy"
            ],
            "operational": [
                "Emphasize real-time or near-real-time data",
                "Highlight exceptions and alerts",
                "Provide detailed drill-down capabilities",
                "Include process flow visualization"
            ]
        }
        return principles.get(audience, [])