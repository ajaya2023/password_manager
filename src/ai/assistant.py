"""
AI助手模块 - 集成OpenAI GPT进行智能密码管理
"""
import openai
import json
from typing import Dict, List, Optional
from datetime import datetime

class AIAssistant:
    """AI密码管理助手"""
    
    def __init__(self, api_key: str, password_manager):
        self.api_key = api_key
        self.pm = password_manager
        openai.api_key = api_key
        
        # 系统提示词
        self.system_prompt = """
        你是一个安全的密码管理助手。你的职责是：
        1. 帮助用户查找和管理密码
        2. 提供密码安全建议
        3. 生成强密码
        4. 回答密码安全相关问题
        
        重要安全规则：
        - 永远不要在响应中显示完整的密码
        - 只提供密码提示或部分信息
        - 确认用户身份后才能执行敏感操作
        - 建议用户定期更新密码
        """
    
    def process_query(self, user_query: str) -> Dict:
        """处理用户查询"""
        if not self.pm.is_unlocked:
            return {
                'success': False,
                'message': '请先解锁密码管理器'
            }
        
        try:
            # 分析用户意图
            intent = self._analyze_intent(user_query)
            
            # 根据意图执行操作
            if intent['action'] == 'search':
                return self._handle_search(intent['parameters'])
            
            elif intent['action'] == 'generate':
                return self._handle_generate(intent['parameters'])
            
            elif intent['action'] == 'security_check':
                return self._handle_security_check()
            
            elif intent['action'] == 'advice':
                return self._handle_advice(user_query)
            
            else:
                return self._handle_general_query(user_query)
                
        except Exception as e:
            return {
                'success': False,
                'message': f'处理请求时出错: {str(e)}'
            }
    
    def _analyze_intent(self, query: str) -> Dict:
        """分析用户意图"""
        query_lower = query.lower()
        
        # 搜索密码
        if any(keyword in query_lower for keyword in ['找', '查找', '搜索', '获取', 'get', 'find']):
            # 提取搜索关键词
            for word in ['密码', 'password', '账号', 'account']:
                if word in query_lower:
                    search_term = query_lower.split(word)[-1].strip()
                    return {
                        'action': 'search',
                        'parameters': {'query': search_term}
                    }
        
        # 生成密码
        elif any(keyword in query_lower for keyword in ['生成', '创建', 'generate', 'create']):
            return {
                'action': 'generate',
                'parameters': self._extract_password_requirements(query)
            }
        
        # 安全检查
        elif any(keyword in query_lower for keyword in ['安全', '检查', 'security', 'check']):
            return {
                'action': 'security_check',
                'parameters': {}
            }
        
        # 建议
        elif any(keyword in query_lower for keyword in ['建议', '推荐', 'advice', 'recommend']):
            return {
                'action': 'advice',
                'parameters': {}
            }
        
        # 默认为一般查询
        return {
            'action': 'general',
            'parameters': {}
        }
    
    def _handle_search(self, parameters: Dict) -> Dict:
        """处理搜索请求"""
        query = parameters.get('query', '')
        results = self.pm.search_passwords(query)
        
        if results:
            # 不返回实际密码，只返回提示信息
            safe_results = []
            for entry in results[:5]:  # 最多返回5个结果
                safe_results.append({
                    'title': entry['title'],
                    'username': entry['username'],
                    'category': entry['category'],
                    'hint': f"密码已保存，上次修改: {entry['last_modified']}"
                })
            
            return {
                'success': True,
                'message': f'找到 {len(results)} 个匹配的密码',
                'results': safe_results
            }
        
        return {
            'success': True,
            'message': '没有找到匹配的密码',
            'results': []
        }
    
    def _handle_generate(self, parameters: Dict) -> Dict:
        """处理生成密码请求"""
        length = parameters.get('length', 16)
        
        # 生成密码
        password = self.pm.generate_password(
            length=length,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_symbols=parameters.get('symbols', True)
        )
        
        # 计算密码强度
        strength = self._calculate_password_strength(password)
        
        return {
            'success': True,
            'message': '已生成新密码',
            'password': password,
            'strength': strength,
            'advice': '建议立即保存此密码到密码管理器中'
        }
    
    def _handle_security_check(self) -> Dict:
        """执行安全检查"""
        all_passwords = self.pm.search_passwords()
        
        issues = []
        
        # 检查弱密码
        weak_passwords = []
        old_passwords = []
        duplicate_passwords = {}
        
        for entry in all_passwords:
            # 获取完整密码信息
            full_entry = self.pm.get_password(entry['id'])
            
            # 检查密码强度
            strength = self._calculate_password_strength(full_entry['password'])
            if strength < 3:
                weak_passwords.append(entry['title'])
            
            # 检查密码年龄
            last_modified = datetime.fromisoformat(entry['last_modified'])
            days_old = (datetime.now() - last_modified).days
            if days_old > 90:
                old_passwords.append({
                    'title': entry['title'],
                    'days': days_old
                })
            
            # 检查重复密码
            pwd_hash = hash(full_entry['password'])
            if pwd_hash in duplicate_passwords:
                duplicate_passwords[pwd_hash].append(entry['title'])
            else:
                duplicate_passwords[pwd_hash] = [entry['title']]
        
        # 生成报告
        report = {
            'total_passwords': len(all_passwords),
            'weak_passwords': len(weak_passwords),
            'old_passwords': len(old_passwords),
            'duplicates': sum(1 for group in duplicate_passwords.values() if len(group) > 1)
        }
        
        recommendations = []
        if weak_passwords:
            recommendations.append(f"建议更新以下弱密码: {', '.join(weak_passwords[:3])}")
        if old_passwords:
            recommendations.append(f"建议更新超过90天的密码: {', '.join([p['title'] for p in old_passwords[:3]])}")
        
        return {
            'success': True,
            'message': '安全检查完成',
            'report': report,
            'recommendations': recommendations
        }
    
    def _calculate_password_strength(self, password: str) -> int:
        """计算密码强度（1-5）"""
        score = 0
        
        # 长度
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # 字符多样性
        import string
        if any(c in string.ascii_lowercase for c in password):
            score += 0.5
        if any(c in string.ascii_uppercase for c in password):
            score += 0.5
        if any(c in string.digits for c in password):
            score += 0.5
        if any(c in string.punctuation for c in password):
            score += 0.5
        
        return min(5, int(score))
    
    def _extract_password_requirements(self, query: str) -> Dict:
        """从查询中提取密码要求"""
        requirements = {
            'length': 16,
            'symbols': True
        }
        
        # 提取长度
        import re
        length_match = re.search(r'\d+', query)
        if length_match:
            requirements['length'] = min(32, max(8, int(length_match.group())))
        
        # 检查是否需要符号
        if '不要符号' in query or 'no symbols' in query.lower():
            requirements['symbols'] = False
        
        return requirements
    
    def _handle_advice(self, query: str) -> Dict:
        """提供密码安全建议"""
        advice = [
            "使用独特的密码：每个账户使用不同的密码",
            "定期更新：每3-6个月更新重要账户的密码",
            "启用双因素认证：为重要账户启用2FA",
            "避免常见密码：不要使用生日、姓名等个人信息",
            "使用密码管理器：让密码管理器生成和存储复杂密码"
        ]
        
        # 继续 assistant.py

        return {
            'success': True,
            'message': '密码安全最佳实践',
            'advice': advice,
            'personalized': self._get_personalized_advice()
        }
    
    def _get_personalized_advice(self) -> List[str]:
        """获取个性化建议"""
        advice = []
        all_passwords = self.pm.search_passwords()
        
        if len(all_passwords) < 5:
            advice.append("建议添加更多常用账户的密码")
        
        # 检查分类使用
        categories = {}
        for entry in all_passwords:
            cat = entry.get('category', 'general')
            categories[cat] = categories.get(cat, 0) + 1
        
        if len(categories) == 1:
            advice.append("建议使用分类功能更好地组织密码")
        
        return advice
    
    def _handle_general_query(self, query: str) -> Dict:
        """处理一般查询"""
        try:
            # 使用GPT处理一般查询
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return {
                'success': True,
                'message': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"AI处理失败: {str(e)}"
            }
