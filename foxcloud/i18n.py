import oslo_i18n


_translators = oslo_i18n.TranslatorFactory(domain='foxcloud')

# The primary translation function using the well-known name "_"
_ = _translators.primary
