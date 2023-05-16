therabody_dic = {   'loginAPI': 'https://API_domain.talkdeskid.com/oauth/token',
                    'baseAPI':  'https://api.talkdeskapp.com',
                    'clientID': 'ea9f8afd8b7c48ba99567c5baf7ff956',
                    'client_secret': '3F1U-QMhuNy_nBUaGtUxTOYHIXdrAWaDOhzYIioz1wTGjRwvQ3oMlm4cR4oPrTex1HPHsMbWGFoFE4eIarrPWw',
                    'SQLschema': 'Talkdesk',
                    'report_types': ['explore_calls', 'ring_attempts', 'contacts', 'user_status']
}

root_dic = {    'loginAPI': 'https://API_domain.talkdeskid.com/oauth/token',
                'baseAPI':  'https://api.talkdeskapp.com',
                'clientID': 'be16049f0dfe4928a0ac13917d72c67c',
                'client_secret': 'FZ6FyzOsKXo7Dk8votP0fuyxiHp5ze68bP99Vb1z6vWKn9IV4wcLlPMUO0MAy_JLPXCEZ49C6r_M5rN-_oGJAw',
                'SQLschema': 'Talkdesk',
                'report_types': ['explore_calls', 'ring_attempts', 'contacts', 'user_status', 'adherence', 'feedback_flow']
}

ultra_dic = {   'loginAPI': 'https://login.usw2.pure.cloud/oauth/token',
                'baseAPI':  'https://api.usw2.pure.cloud/api/v2',
                'clientID': 'e22d4f86-c236-4898-a566-fedfc9d666aa',
                'client_secret': 'MKMNw3DtTBWTtLluWMSGGsgmtCA5JTh_z1j2_5BnA6U',
                'SQLschema': 'Genesys',
                'report_types': ['users_presence', 'conversations'],
                'dict_columns': {
                                'conversations_segments': [ 'conversationId', 
                                                            'participants.participantId',
                                                            'participants.sessions.segments.disconnectType',
                                                            'participants.sessions.segments.segmentEnd',
                                                            'participants.sessions.segments.segmentStart',
                                                            'participants.sessions.segments.segmentType',
                                                            'participants.sessions.segments.wrapUpCode',
                                                            'participants.sessions.segments.wrapUpNote'
                                ],
                                'conversations_metrics': [  'conversationId', 
                                                            'participants.participantId',
                                                            'participants.sessions.metrics.emitDate',
                                                            'participants.sessions.metrics.name',
                                                            'participants.sessions.metrics.value'
                                ],
                                'conversations_participants': [
                                                                'conversationId', 
                                                                'participants.participantId', 
                                                                'participants.participantName',
                                                                'participants.purpose', 
                                                                'participants.userId',
                                                                'participants.sessions.activeSkillIds',
                                                                'participants.sessions.direction', 
                                                                'participants.sessions.flowInType',
                                                                'participants.sessions.mediaType', 
                                                                'participants.sessions.remote',
                                                                'participants.sessions.remoteNameDisplayable',
                                                                'participants.sessions.selectedAgentId'
                                ],
                                'conversations': [
                                                    'conversationId',                                                 
                                                    'conversationEnd', 
                                                    'conversationStart', 
                                                    'divisionIds',
                                                    'mediaStatsMinConversationMos', 
                                                    'mediaStatsMinConversationRFactor',
                                                    'originatingDirection'
                                ],
                                'users_presence': [
                                                    'users_presence_id',
                                                    'userId',                                                 
                                                    'primaryPresence.startTime', 
                                                    'primaryPresence.endTime', 
                                                    'primaryPresence.systemPresence'
                                ],
                                'queues': [
                                                'id',
                                                'name',
                                                'dateCreated',
                                                'dateModified',
                                                'modifiedBy',
                                                'createdBy',
                                                'memberCount',
                                                'userMemberCount',
                                                'skillEvaluationMethod',
                                                'autoAnswerOnly',
                                                'enableTranscription',
                                                'enableManualAssignment',
                                                'acwSettings.timeoutMs',
                                                'acwSettings.wrapupPrompt',
                                                'mediaSettings.call.alertingTimeoutSeconds',
                                                'mediaSettings.call.serviceLevel.percentage',
                                                'mediaSettings.call.serviceLevel.durationMs',
                                                'mediaSettings.callback.alertingTimeoutSeconds',
                                                'mediaSettings.callback.serviceLevel.percentage',
                                                'mediaSettings.callback.serviceLevel.durationMs',
                                                'mediaSettings.chat.alertingTimeoutSeconds',
                                                'mediaSettings.chat.serviceLevel.percentage',
                                                'mediaSettings.chat.serviceLevel.durationMs',
                                                'mediaSettings.email.alertingTimeoutSeconds',
                                                'mediaSettings.email.serviceLevel.percentage',
                                                'mediaSettings.email.serviceLevel.durationMs',
                                                'mediaSettings.message.alertingTimeoutSeconds',
                                                'mediaSettings.message.serviceLevel.percentage',
                                                'mediaSettings.message.serviceLevel.durationMs'
                                ]
                                }
}

kustomer_dic = {    'baseAPI':  'https://api.kustomerapp.com/v1',
                    'searchAPI':  'https://api.kustomerapp.com/v1/customers/search',
                    'API_key':  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0MTljNmEyM2Y3NDljN2Y2ZjBhNDNjMiIsInVzZXIiOiI2NDE5YzZhMTJmMDQ4MDU1Y2ExZjYwNmEiLCJvcmciOiI1ZmVkZWU4MjdkYWYyY2ZlMWE4M2U5Y2UiLCJvcmdOYW1lIjoiam9pbnJvb3QiLCJ1c2VyVHlwZSI6Im1hY2hpbmUiLCJwb2QiOiJwcm9kMSIsInJvbGVzIjpbIm9yZy5hZG1pbiIsIm9yZy5hZG1pbi51c2VyIiwib3JnLmFkbWluLnVzZXIucmVhZCIsIm9yZy5wZXJtaXNzaW9uLmFuYWx5dGljcyIsIm9yZy5wZXJtaXNzaW9uLmFuYWx5dGljcy5yZWFkIiwib3JnLnBlcm1pc3Npb24uYXR0YWNobWVudC5yZWFkIiwib3JnLnBlcm1pc3Npb24uY29udmVyc2F0aW9uLnJlYWQiLCJvcmcucGVybWlzc2lvbi5tZXNzYWdlLnJlYWQiLCJvcmcucGVybWlzc2lvbi5tZXRhZGF0YS5yZWFkIiwib3JnLnBlcm1pc3Npb24ubWV0YWRhdGFfc2Vuc2l0aXZlLnJlYWQiLCJvcmcucGVybWlzc2lvbi5ub3RlLnJlYWQiLCJvcmcucGVybWlzc2lvbi5xdWV1ZS5yZWFkIiwib3JnLnBlcm1pc3Npb24ucmVhZCIsIm9yZy5wZXJtaXNzaW9uLnJvdXRpbmcucmVhZCIsIm9yZy5wZXJtaXNzaW9uLnJvdXRpbmdfc3RhdHVzLnJlYWQiLCJvcmcucGVybWlzc2lvbi5zYXRpc2ZhY3Rpb24ucmVhZCIsIm9yZy5wZXJtaXNzaW9uLnNjaGVkdWxlLnJlYWQiLCJvcmcucGVybWlzc2lvbi5zZWFyY2guY3JlYXRlIiwib3JnLnBlcm1pc3Npb24uc2VhcmNoLnJlYWQiLCJvcmcucGVybWlzc2lvbi5zbGEucmVhZCIsIm9yZy5wZXJtaXNzaW9uLnVzZXIiLCJvcmcucGVybWlzc2lvbi51c2VyLnJlYWQiLCJvcmcucGVybWlzc2lvbi51c2VyX2FjdGl2aXR5LnJlYWQiLCJvcmcucGVybWlzc2lvbi51c2VyX3BlcmZvcm1hbmNlLnJlYWQiLCJvcmcucGVybWlzc2lvbi53b3JrX2l0ZW0ucmVhZCIsIm9yZy5wZXJtaXNzaW9uLndvcmtfc2Vzc2lvbi5yZWFkIiwib3JnLnBlcm1pc3Npb24ud29ya2Zsb3cucmVhZCJdLCJhdWQiOiJ1cm46Y29uc3VtZXIiLCJpc3MiOiJ1cm46YXBpIiwic3ViIjoiNjQxOWM2YTEyZjA0ODA1NWNhMWY2MDZhIn0.NMJK2mYcwXnjXGv9HqkP26I1wqi_Hg3oYL2iMQIfQ6s',
                    'SQLschema': 'Kustomer',
                    'report_types':['conversation', 'message', 'note', 'conversation_time', 'work_item', 'work_session'], # 'work-sessions', 'work-items', 'users', 'sla', 'satisfaction']
                    'reference_maxDate': ['updatedAt', 'updatedAt', 'updatedAt', 'handleAt', 'updatedAt', 'updatedAt'],
                    'dict_columns': {
                                'users':[   'type', 'id', 'attributes.createdAt', 'attributes.deletedAt', 'attributes.displayName',
                                            'attributes.email', 'attributes.emailVerifiedAt', 'attributes.firstEmailVerifiedAt',
                                            'attributes.firstLoginAt', 'attributes.isEmailValid',
                                            'attributes.mobile', 'attributes.modifiedAt', 'attributes.name',
                                            'attributes.updatedAt', 'attributes.userType',
                                            'attributes.verifiedEmailStatus'    
                                ],
                                'conversation': [   'type', 'id', 'attributes.assignedTeams', 'attributes.assignedUsers',
                                                    'attributes.assistant.assistantId', 'attributes.assistant.status',
                                                    'attributes.assistant.transferredAt', 'attributes.createdAt',
                                                    'attributes.custom.conversationCategoryTree', 'attributes.custom.customerServiceTree',
                                                    'attributes.defaultLang', 'attributes.direction', 'attributes.doneCount', 'attributes.ended',
                                                    'attributes.endedAt', 'attributes.endedByType', 'attributes.endedReason',
                                                    'attributes.firstDone.assignedTeams', 'attributes.firstDone.assignedUsers',
                                                    'attributes.firstDone.businessTime', 'attributes.firstDone.createdAt',
                                                    'attributes.firstDone.createdBy', 'attributes.firstDone.lastMessageDirection',
                                                    'attributes.firstDone.lastMessageDirectionType', 'attributes.firstDone.messageCount',
                                                    'attributes.firstDone.messageCountByChannel.chat', 'attributes.firstDone.messageCountByChannel.email',
                                                    'attributes.firstDone.messageCountByChannel.voice', 'attributes.firstDone.noteCount',
                                                    'attributes.firstDone.outboundMessageCount', 'attributes.firstDone.outboundMessageCountByChannel.chat',
                                                    'attributes.firstDone.time', 'attributes.firstMessageIn.channel', 'attributes.firstMessageIn.createdAt',
                                                    'attributes.firstMessageIn.directionType', 'attributes.firstMessageIn.firstDelivered.clientType',
                                                    'attributes.firstMessageIn.firstDelivered.clientVersion', 'attributes.firstMessageIn.firstDelivered.timestamp',
                                                    'attributes.firstMessageIn.id', 'attributes.firstMessageIn.meta.placedAt', 'attributes.firstMessageIn.sentAt',
                                                    'attributes.firstMessageOut.channel', 'attributes.firstMessageOut.createdAt', 'attributes.firstMessageOut.createdBy',
                                                    'attributes.firstMessageOut.directionType', 'attributes.firstMessageOut.id', 'attributes.firstMessageOut.sentAt',
                                                    'attributes.firstResponse.assignedTeams', 'attributes.firstResponse.assignedUsers',
                                                    'attributes.firstResponse.businessTime', 'attributes.firstResponse.createdAt', 'attributes.firstResponse.createdBy',
                                                    'attributes.firstResponse.id', 'attributes.firstResponse.responseTime', 'attributes.firstResponse.sentAt',
                                                    'attributes.firstResponse.time', 'attributes.firstResponseSinceLastDone.assignedTeams',
                                                    'attributes.firstResponseSinceLastDone.assignedUsers', 'attributes.firstResponseSinceLastDone.businessTime',
                                                    'attributes.firstResponseSinceLastDone.createdAt', 'attributes.firstResponseSinceLastDone.createdBy',
                                                    'attributes.firstResponseSinceLastDone.id', 'attributes.firstResponseSinceLastDone.responseTime',
                                                    'attributes.firstResponseSinceLastDone.sentAt', 'attributes.firstResponseSinceLastDone.time', 'attributes.importedAt',
                                                    'attributes.inboundMessageCount', 'attributes.lastActivityAt', 'attributes.lastDone.assignedTeams',
                                                    'attributes.lastDone.assignedUsers', 'attributes.lastDone.businessTime', 'attributes.lastDone.createdAt',
                                                    'attributes.lastDone.createdBy', 'attributes.lastDone.lastMessageDirection', 'attributes.lastDone.lastMessageDirectionType',
                                                    'attributes.lastDone.messageCount', 'attributes.lastDone.messageCountByChannel.chat',
                                                    'attributes.lastDone.messageCountByChannel.email', 'attributes.lastDone.messageCountByChannel.voice',
                                                    'attributes.lastDone.noteCount', 'attributes.lastDone.outboundMessageCount', 'attributes.lastDone.outboundMessageCountByChannel.chat',
                                                    'attributes.lastDone.outboundMessageCountByChannel.email', 'attributes.lastDone.time', 'attributes.lastMessageAt',
                                                    'attributes.lastMessageDirection', 'attributes.lastMessageIn.channel', 'attributes.lastMessageIn.createdAt',
                                                    'attributes.lastMessageIn.id', 'attributes.lastMessageIn.meta.placedAt', 'attributes.lastMessageIn.sentAt',
                                                    'attributes.lastMessageOut.createdAt', 'attributes.lastMessageOut.createdBy', 'attributes.lastMessageOut.id',
                                                    'attributes.lastMessageOut.sentAt', 'attributes.lastMessageUnrespondedTo.createdAt', 'attributes.lastMessageUnrespondedTo.id',
                                                    'attributes.lastMessageUnrespondedTo.sentAt', 'attributes.lastMessageUnrespondedToSinceLastDone.createdAt',
                                                    'attributes.lastMessageUnrespondedToSinceLastDone.id', 'attributes.lastMessageUnrespondedToSinceLastDone.sentAt',
                                                    'attributes.lastReceivedAt', 'attributes.lastResponse.assignedTeams', 'attributes.lastResponse.assignedUsers',
                                                    'attributes.lastResponse.businessTime', 'attributes.lastResponse.createdAt', 'attributes.lastResponse.createdBy',
                                                    'attributes.lastResponse.id', 'attributes.lastResponse.time', 'attributes.locale', 'attributes.messageCount', 'attributes.modifiedAt',
                                                    'attributes.noteCount', 'attributes.open.statusAt', 'attributes.outboundMessageCount', 'attributes.phase', 'attributes.preview',
                                                    'attributes.priority', 'attributes.reopenCount', 'attributes.rev', 'attributes.satisfaction',
                                                    'attributes.satisfactionLevel.channel', 'attributes.satisfactionLevel.createdAt',
                                                    'attributes.satisfactionLevel.scheduledFor', 'attributes.satisfactionLevel.sentAt',
                                                    'attributes.satisfactionLevel.sentBy', 'attributes.satisfactionLevel.status', 'attributes.satisfactionLevel.updatedAt',
                                                    'attributes.sla.breached', 'attributes.sla.matchedAt', 'attributes.sla.name', 'attributes.sla.status', 'attributes.sla.summary.firstBreachAt',
                                                    'attributes.sla.summary.satisfiedAt', 'attributes.sla.version', 'attributes.snooze.status', 'attributes.snooze.statusAt', 'attributes.snooze.time',
                                                    'attributes.snoozeCount', 'attributes.spam', 'attributes.status', 'attributes.totalDone.businessTime',
                                                    'attributes.totalDone.time', 'attributes.totalOpen.businessTime', 'attributes.totalOpen.businessTimeBySchedule',
                                                    'attributes.totalOpen.businessTimeByScheduleSinceLastDone', 'attributes.totalOpen.businessTimeSinceLastDone', 'attributes.totalOpen.time',
                                                    'attributes.totalOpen.timeSinceLastDone', 'attributes.totalSnooze.businessTime', 'attributes.totalSnooze.time', 'attributes.updatedAt',
                                                    'relationships.createdBy.data.id', 'relationships.createdBy.data.type', 'relationships.customer.data.id', 'relationships.customer.data.type',
                                                    'relationships.endedBy.data.id', 'relationships.endedBy.data.type', 'relationships.modifiedBy.data.id', 'relationships.modifiedBy.data.type',
                                                    'relationships.queue.data.id', 'relationships.queue.data.type', 'relationships.sla.data.id', 'relationships.sla.data.type',
                                                    'relationships.slaVersion.data.id', 'relationships.slaVersion.data.type'
                                ],
                                'conversation_time': [  'type', 'id', 'attributes.assignedTeams', 'attributes.assignedUsers', 'attributes.createdAt', 'attributes.handleAt',
                                                        'attributes.handlePauseAt', 'attributes.handlePauseBy', 'attributes.handleTime', 'attributes.messageAt', 'attributes.messageTime', 'attributes.noteAt',
                                                        'attributes.noteTime', 'relationships.conversation.data.id', 'relationships.createdBy.data.id', 'relationships.customer.data.id'
                                ],
                                'work_item': [  'id', 'type', 'attributes.channel', 'attributes.completedAt', 'attributes.createdAt', 'attributes.firstEnterQueueAt', 'attributes.itemSize', 'attributes.modifiedAt',
                                                'attributes.paused', 'attributes.priority', 'attributes.queuedCount', 'attributes.resourceCreatedAt', 'attributes.resourceDirection',
                                                'attributes.resourceFirstAssignTime', 'attributes.resourceFirstQueueTime', 'attributes.resourceFirstRouteTime', 'attributes.resourceRev', 'attributes.resourceType',
                                                'attributes.rev', 'attributes.status',  'attributes.updatedAt', 'attributes.workItemNumber', 'attributes.firstRoutedResponse.businessTime',
                                                'attributes.firstRoutedResponse.createdAt', 'attributes.firstRoutedResponse.id', 'attributes.firstRoutedResponse.time', 'attributes.handle.businessTime',
                                                'attributes.handle.completedAt', 'attributes.handle.time', 'attributes.ivr.businessTime', 'attributes.ivr.time', 'attributes.lastRevision.acceptedAt',
                                                'attributes.lastRevision.enteredQueueAt', 'attributes.lastRevision.queueBusinessTime', 'attributes.lastRevision.queueTime', 'attributes.lastRevision.routedAt',
                                                'attributes.resource.id', 'attributes.resource.lastMessageUnrespondedToSentAt', 'attributes.resource.priority', 'attributes.resource.status',
                                                'attributes.wrapUp.businessTime', 'attributes.wrapUp.enteredAt', 'attributes.wrapUp.time', 'attributes.resource.sla.breachAt', 'relationships.acceptedBy.data.id',
                                                'relationships.acceptedBy.data.type', 'relationships.assignedTo.data.id', 'relationships.assignedTo.data.type', 'relationships.lastRevision.data.id',
                                                'relationships.lastRevision.data.type', 'relationships.modifiedBy.data.id', 'relationships.modifiedBy.data.type', 'relationships.queue.data.id',
                                                'relationships.queue.data.type', 'relationships.resource.data.id', 'relationships.resource.data.type', 'relationships.routedTo.data.id',
                                                'relationships.routedTo.data.type', 'relationships.routedToSession.data.id', 'relationships.routedToSession.data.type',
                                                'relationships.team.data.id', 'relationships.team.data.type', 'relationships.workSession.data.id', 'relationships.workSession.data.type'
                                ],
                                'work_session': [       'id', 'type', 'attributes.capacityRemaining', 'attributes.capacityStatus', 'attributes.createdAt', 'attributes.handledConversationCount', 'attributes.handledItemCount',
                                                        'attributes.hasPendingItem', 'attributes.hasSkills', 'attributes.idleSince', 'attributes.lastAssignedItemAt', 'attributes.modifiedAt', 'attributes.pausedWorkItemCount',
                                                        'attributes.rev', 'attributes.routable', 'attributes.signedInAt', 'attributes.signedOutAt', 'attributes.statusType', 'attributes.subsystem',
                                                        'attributes.totalCapacity', 'attributes.updatedAt', 'attributes.userNameKeyword', 'attributes.workItemCount', 'attributes.lastRevision.handledItemCount',
                                                        'attributes.totalAvailable.businessTime', 'attributes.totalAvailable.statusAt', 'attributes.totalAvailable.time', 'attributes.totalAvailableAtCapacity.businessTime',
                                                        'attributes.totalAvailableAtCapacity.time', 'attributes.totalAvailableIdleCapacity.businessTime', 'attributes.totalAvailableIdleCapacity.time',
                                                        'attributes.totalAvailableNotAtCapacity.businessTime', 'attributes.totalAvailableNotAtCapacity.time', 'attributes.totalUnavailable.businessTime',
                                                        'attributes.totalUnavailable.statusAt', 'attributes.totalUnavailable.time', 'attributes.totalUnavailableAtCapacity.businessTime',
                                                        'attributes.totalUnavailableAtCapacity.time', 'attributes.totalUnavailableIdleCapacity.businessTime', 'attributes.totalUnavailableIdleCapacity.time',
                                                        'attributes.totalUnavailableNotAtCapacity.businessTime', 'attributes.totalUnavailableNotAtCapacity.time', 'attributes.lastRevision.totalAvailable.statusAt',
                                                        'attributes.lastRevision.totalUnavailable.statusAt', 'relationships.lastRevision.data.id', 'relationships.lastRevision.data.type', 'relationships.modifiedBy.data.id',
                                                        'relationships.modifiedBy.data.type', 'relationships.routingSettings.data.id',
                                                        'relationships.routingSettings.data.type', 'relationships.status.data.id',  'relationships.status.data.type', 'relationships.team.data.id', 'relationships.team.data.type',
                                                        'relationships.user.data.id', 'relationships.user.data.type', 'relationships.queues.data.id', 'relationships.queues.data.type'
                                ],
                                'message': [    'type',	'id', 'attributes.app',	'attributes.channel', 'attributes.createdAt', 'attributes.direction',
	                                        'attributes.modifiedAt', 'attributes.preview', 'attributes.responseBusinessTime',
                                                'attributes.responseTime', 'attributes.rev', 'attributes.sentAt', 'attributes.status',
                                                'attributes.subject', 'attributes.updatedAt', 'attributes.firstDelivered.clientType',
                                                'attributes.firstDelivered.timestamp', 'attributes.firstRead.timestamp', 'attributes.meta.answeredAt',
                                                'attributes.meta.endedAt', 'relationships.conversation.data.id', 'relationships.createdBy.data.id',
                                                'relationships.customer.data.id', 'relationships.modifiedBy.data.id'
                                ],
                                'note': [   'type', 'id', 'attributes.body', 'attributes.createdAt', 'attributes.modifiedAt', 'attributes.updatedAt', 'relationships.conversation.data.id',
                                            'relationships.conversation.data.type', 'relationships.createdBy.data.id', 'relationships.createdBy.data.type', 'relationships.customer.data.id',
                                            'relationships.customer.data.type', 'relationships.modifiedBy.data.id', 'relationships.modifiedBy.data.type'
                                ],
                                'teams':[       'type',	'id', 'attributes.createdAt', 'attributes.deleted', 'attributes.deletedAt', 'attributes.displayName', 'attributes.icon', 'attributes.modifiedAt',
                                                'attributes.name', 'attributes.updatedAt' 
                                ],
                                'queues':[      'id', 'type', 'attributes.createdAt', 'attributes.deleted', 'attributes.description', 'attributes.displayName', 'attributes.itemSize', 'attributes.modifiedAt',
                                                'attributes.name', 'attributes.priority', 'attributes.restrictTransfersByUsers', 'attributes.system', 'attributes.updatedAt'
                                ]
                        }
}