# Atlas v4.1 阶段5：Dead Module Report（产品减法）

> 自动扫描：桌面/后端入口实际引用 vs engine 全部模块
> 日期：2026-08-03

## 统计
- engine 模块总数：142
- 被入口实际使用：26
- **未被使用（疑似 Dead）：116**

## 被使用模块（26）
action, assistant, autonomous_maintenance, budget_manager, chase_analysis, daily_intelligence, data_center_v2, decision, evaluation, evaluation_v2, export, intelligence, lottery_intent, lottery_quant, observability, onboarding, personal_growth, personal_review, reminder_center, report_center, ticket_system, user_behavior, user_feedback_v2, user_intelligence, user_memory, value_score

## Dead 模块清单（121，禁止删除，归档处理）

1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
9. 
10. 
11. 
12. 
13. 
14. 
15. 
16. 
17. 
18. 
19. 
20. 
21. 
22. 
23. 
24. 
25. 
26. 
27. 
28. 
29. 
30. 
31. 
32. 
33. 
34. 
35. 
36. 
37. 
38. 
39. 
40. 
41. 
42. 
43. 
44. 
45. 
46. 
47. 
48. 
49. 
50. 
51. 
52. 
53. 
54. 
55. 
56. 
57. 
58. 
59. 
60. 
61. 
62. 
63. 
64. 
65. 
66. 
67. 
68. 
69. 
70. 
71. 
72. 
73. 
74. 
75. 
76. 
77. 
78. 
79. 
80. 
81. 
82. 
83. 
84. 
85. 
86. 
87. 
88. 
89. 
90. 
91. 
92. 
93. 
94. 
95. 
96. 
97. 
98. 
99. 
100. 
101. 
102. 
103. 
104. 
105. 
106. 
107. 
108. 
109. 
110. 
111. 
112. 
113. 
114. 
115. 
116. 

## 结论
- 121 个模块无任何桌面/后端入口，属早期多智能体实验残留
- **禁止删除**（可能被未来复用），先归档本报告
- 产品叙事聚焦 26 个被使用模块，121 个标记为 legacy 冻结

*生成：Dead Module 自动扫描脚本*