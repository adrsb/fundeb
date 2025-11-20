from pathlib import Path

from pandera.typing.pandas import Series
from pandera.pandas import DataFrameModel, Field
import pandera.pandas as pa


class CurrentAccountCsvValidatorInputSchema(DataFrameModel):
    BANCO: Series[str] = Field(isin=["001"], nullable=False)
    AGENCIA: Series[str]
    CONTA: Series[str]
    ENDERECO_AGENCIA: Series[str]
    DT_ABERTURA: Series[pa.DateTime]
    NOME_TITURAL: Series[str]
    CNPJ_TITURAL: Series[str]
    UF: Series[str] = Field(str_length={"min_value": 2, "max_value": 2})
    MUNICIPIO: Series[str]
    NOME_RESPONSAVEL_LEGAL: Series[str]
    CPF_RESPONSAVEL_LEGAL: Series[str]
    DATA_INICIO: Series[pa.DateTime]
    DATA_FIM: Series[pa.DateTime]
    SALDO_ANTERIOR_CC: Series[float] = Field(ge=0)
    SALDO_ANTERIOR_APLICACAO: Series[float] = Field(ge=0)
    SALDO_ANTERIOR_TOTAL: Series[float] = Field(ge=0)
    DT_LANCAMENTO: Series[pa.DateTime]
    NOME_DESTINATARIO_DEPOSITANTE: Series[str] = Field(nullable=True)
    CPF_CNPJ: Series[str] = Field(nullable=True)
    HISTORICO_FINALIDADE: Series[str]
    VALOR: Series[float] = Field(ge=0, nullable=False)
    D_C: Series[str] = Field(isin=["D", "C"])
    SALDO_ATUAL_CC: Series[float] = Field(ge=0)
    SALDO_ATUAL_APLICACAO: Series[float] = Field(ge=0)
    SALDO_ATUAL_TOTAL: Series[float] = Field(ge=0)

    class Config:
        strict = True  # Não aceita colunas extras


if __name__ == "__main__":
    from fundeb.ingestion.csv_loader import CsvLoader
    from fundeb.config.settings import settings

    extractor = CsvLoader(extractors_config_path=settings.extractors_config_path)
    file_path_test = Path(
        r"C:\Users\adrsb\OneDrive\Documentos\Projects\FundebProject\data\raw"
        r"\external\bb\conta_corrente\csv\EXTRATO_BANCARIO_CC_AP_MACAPA_2025_01.csv"
    )
    extractor.get_params("conta_corrente", "csv")
    df = extractor.load_data(file_path_test)
    df_validado = CurrentAccountCsvValidatorInputSchema.validate(df)
    display(df)  # type: ignore # noqa: F821
