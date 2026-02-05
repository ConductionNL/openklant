<template>
	<div id="openklant-app">
		<NcEmptyContent
			:name="t('openklant', 'OpenKlant')"
			:description="t('openklant', 'Customer interaction management for Nextcloud')">
			<template #icon>
				<AccountGroupIcon :size="64" />
			</template>
		</NcEmptyContent>
	</div>
</template>

<script>
import { NcEmptyContent } from '@nextcloud/vue'
import AccountGroupIcon from 'vue-material-design-icons/AccountGroup.vue'

export default {
	name: 'App',
	components: {
		NcEmptyContent,
		AccountGroupIcon,
	},
}
</script>
