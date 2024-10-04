import json

from openai import AsyncOpenAI

AVAILABLE_FUNCTIONS = {}

INSTRUCTIONS = [
    """You are a tax preparer. You have been asked to save the tax information from the 1099-DIV form. The 1099-DIV form is a tax form used to report dividends and distributions received by individuals during the tax year. This information is used to prepare the employee's tax return.
<RULES>
- Avoid hallucinations.
- It is mandatory to fill all the fields. Use 0 and empty strings if the information is not available.
- The form 1099-DIV is a tax form used to report dividends and distributions received by individuals during the tax year.
- It is mandatory to include all the payer's information individually.
- You can sum up the funcd details if multiple funds are associated with one payer.
- It is mandatory to respond in below json format:
```
{
    "form_1099_div_data": [
        {
            "payer_s_name": "",
            "payer_s_federal_id_number": 0,
            "account_number": 0,
            "1a_total_ordinary_dividends": 0,
            "1b_qualified_dividends": 0,
            "2a_total_capital_gain_distr": 0,
            "2b_unrecap_sec_1250_gain": 0,
            "2c_section_1202_gain": 0,
            "2d_collectibles_28_gain": 0,
            "3_nondividend_distributions": 0,
            "4_federal_income_tax_withheld": 0,
            "5_section_199a_dividends": 0,
            "6_investment_expenses": 0,
            "7_foreign_tax_paid": 0,
            "8_foreign_country_or_us_possession": "",
            "9_cash_liquidation_distributions":0,
            "10_noncash_liquidation_distributions": 0,
            "11_fatca_filing_requirement": "",
            "12_exempt_interest_dividends": 0,
            "13_specified_private_activity_bond_interest_dividends": 0,
            "14_state": "",
            "15_state_identification_no": "",
            "16_state_tax_withheld": 0,
        },
        // Add all the objects here
    ]
}
```
</RULES>
""",
    """You are a tax preparer. You have been asked to save the tax information from the W2 form. The W2 form is a tax form used for reporting wages paid to employees and the taxes withheld from them. This information is used to prepare the employee's tax return.
<RULES>
- Avoid hallucinations.
- It is mandatory to fill all the fields. Use 0 and empty strings if the information is not available.
- The W2 form is a tax form used for reporting wages paid to employees and the taxes withheld from them.
- Avoid duplicate objects in form_w2_data.
- The form_w2_data may contain duplicate objects. So first you have to remove the duplicate objects.
- The data is in the tabular format so you have to read the data according to the table format.
- You have to extract the values only for those columns which are required.
- 12th column have 4 parts (12a, 12b, 12c, and 12d), you have to extract only 12a and 12b values. It is mandatory to extract the 12a and 12b values.
- It is mandatory to respond in below json format:
```
{
    "form_w2_data": {
        "employer_s_name": {
            "taxpayer": ["", // Add all the employer's names here],
            "spouse": ["", // Add all the employer's names here],
            "totals": Total of all the values here
        },
        "1_wages_tips_other_compensation": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "2_federal_income_tax_withheld": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "3_social_security_wages": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "4_social_security_tax_withheld": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "5_medicare_wages_and_tips": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "6_medicare_tax_withheld": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "7_social_security_tips": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "8_allocated_tips": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "10_dependent_care_benefits": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "11_nonqualified_plans": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "12a_non_taxable_combat_pay_code_12q": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "12b_see_instructions_for_box_12": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "13_stat_emp_retire_3rd_party_sick": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "14_other": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "14_railroad_retire_rrta_compensation": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "14_rrta_medicare_tax_withheld_see_form_ct2": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "15_state_employers_state_id_number": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals":  Total of all the values here
        },
        "16_state_wages_tips_etc": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "17_state_income_tax": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "18_local_wages_tips_etc": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "19_local_income_tax": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals": Total of all the values here
        },
        "20_locality_name": {
            "taxpayer": [0, // Add all the values here],
            "spouse": [0, // Add all the values here],
            "totals":  Total of all the values here
        }
    }
}
```
</RULES>
""",
    """You are a tax preparer. You have been asked to save the tax information from the 1099-INT form. A 1099-INT tax form is a record that a person or entity paid you interest during the tax year.
<RULES>
- Avoid hallucinations.
- It is mandatory to fill all the fields. Use 0 and empty strings if the information is not available.
- A 1099-INT tax form is a record that a person or entity paid you interest during the tax year.
- It is mandatory to include all the payer's information individually.
- It is mandatory to respond in below json format:
```
{
    "form_1099_int_data": [
        {
            "payer_s_name": "",
            "payer_s_federal_id_number": "",
            "account_number": "",
            "1_interest_income": 0,
            "2_early_withdrawal_penalty": 0,
            "3_interest_on_us_savings_bonds_and_treas_obligations": 0,
            "4_federal_income_tax_withheld": 0,
            "5_investment_expenses": 0,
            "6_foreign_tax_paid": 0,
            "7_foreign_country_or_us_possession": "",
            "8_tax_exempt_interest": 0,
            "9_specified_private_activity_bond_interest": 0,
            "10_market_discount": 0,
            "11_bond_premium": 0,
            "12_bond_premium_on_treasury_obligations": 0,
            "13_bond_premium_on_tax_exempt_bond":0,
            "14_tax_exempt_and_tax_credit_bond_cusip_no": "",
            "15_state": "",
            "16_state_identification_no": "",
            "17_state_tax_withheld": 0
        },
        // Add all the objects here
    ]
}
```
</RULES>
""",
]


class OpenAIClient:
    def __init__(
        self,
        instruction_no: int,
        model: str = "gpt-4o-2024-08-06",
        timeout: int = 60,
        max_retries: int = 5,
    ):
        self._client = AsyncOpenAI(
            timeout=timeout,
            max_retries=max_retries,
        )
        self._model = model
        self._instructions = INSTRUCTIONS[instruction_no]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._client.close()

    async def create_chat_completions(self, messages: list[dict] = []):
        messages_list = [{"role": "system", "content": self._instructions}]
        messages_list.extend(messages)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages_list,
            response_format={"type": "json_object"},
            stream=True,
        )
        tool_call_response = None
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
            elif delta:
                if not tool_call_response:
                    tool_call_response = delta
                if not tool_call_response.tool_calls and delta.tool_calls:
                    tool_call_response.tool_calls = delta.tool_calls
                if (
                    tool_call_response
                    and delta.tool_calls
                    and len(tool_call_response.tool_calls)
                    < delta.tool_calls[0].index + 1
                ):
                    tool_call_response.tool_calls.append(delta.tool_calls[0])
                tool_call_response = await self._parse_response(
                    delta=delta, tool_call_response=tool_call_response
                )
        if tool_call_response and tool_call_response.tool_calls:
            tool_calls_output = await self._handle_required_action(
                tool_calls=tool_call_response.tool_calls,
            )
            messages.append(tool_call_response)
            messages.extend(tool_calls_output)
            async for chunk in self.create_chat_completions(messages=messages):
                yield chunk

    async def _handle_required_action(self, tool_calls: list[dict]):
        tool_calls_output = []
        for tool in tool_calls:
            if tool.type == "function":
                function_to_call = AVAILABLE_FUNCTIONS[tool.function.name]
                function_arguments = (
                    json.loads(tool.function.arguments)
                    if tool.function.arguments
                    else {}
                )
                function_response = await function_to_call(
                    function_arguments=function_arguments
                )
                tool_calls_output.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool.id,
                        "name": tool.function.name,
                        "content": (
                            str(function_response)
                            if function_response
                            else "No results found."
                        ),
                    }
                )
        return tool_calls_output

    async def _parse_response(self, delta, tool_call_response):
        if delta and delta.tool_calls:
            tool_call_chunk_list = delta.tool_calls
            for tool_call_chunk in tool_call_chunk_list:
                tool_call = tool_call_response.tool_calls[tool_call_chunk.index]
                if tool_call_chunk.function.arguments:
                    tool_call.function.arguments += tool_call_chunk.function.arguments
                    tool_call_response.tool_calls[tool_call_chunk.index] = tool_call
        return tool_call_response
