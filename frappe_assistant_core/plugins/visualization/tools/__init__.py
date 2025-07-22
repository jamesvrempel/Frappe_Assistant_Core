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
Visualization Plugin Tools

Core tools for dashboard and chart creation:
- create_chart: Individual chart creation
- create_kpi_card: KPI metric cards  
- create_insights_dashboard: Dashboard creation and management
- list_user_dashboards: List accessible dashboards
- clone_dashboard: Clone existing dashboards
- create_dashboard_from_template: Template-based dashboard creation
- list_dashboard_templates: Available template listing
- chart_recommendations: Data discovery & suggestions
- create_bi_dashboard: Professional BI dashboards
- get_bi_recommendations: Industry-standard BI recommendations
"""

# Import all tools for easy access
from .create_chart import *
from .create_kpi_card import *
from .create_insights_dashboard import *
from .list_user_dashboards import *
from .clone_dashboard import *
from .create_dashboard_from_template import *
from .list_dashboard_templates import *
from .chart_recommendations import *
from .create_bi_dashboard import *
from .get_bi_recommendations import *